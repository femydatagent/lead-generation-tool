import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

// =====================================================
// LEAD PROCESSING EDGE FUNCTION
// =====================================================

interface LeadJobRequest {
  business_type: string;
  location: string;
  job_name?: string;
}

interface GoogleMapsResult {
  title: string;
  address?: string;
  phone?: string;
  website?: string;
  rating?: number;
  reviews?: number;
}

interface EnrichedLead extends GoogleMapsResult {
  instagram_url?: string;
  instagram_confidence?: number;
  cnpj?: string;
  cnpj_confidence?: number;
  extraction_quality_score?: number;
}

// Initialize Supabase client
const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// API Keys (these should be stored encrypted in the database)
const SERPAPI_KEY = Deno.env.get('SERPAPI_API_KEY');
const DATASTONE_KEY = Deno.env.get('DATASTONE_API_TOKEN');

Deno.serve(async (req: Request) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      },
    });
  }

  try {
    // Get user from JWT token
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      throw new Error('No authorization header');
    }

    const { data: { user }, error: authError } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    );

    if (authError || !user) {
      throw new Error('Invalid token');
    }

    // Parse request body
    const { business_type, location, job_name }: LeadJobRequest = await req.json();

    if (!business_type || !location) {
      throw new Error('business_type and location are required');
    }

    // Create job record
    const { data: job, error: jobError } = await supabase
      .from('lead_jobs')
      .insert({
        user_id: user.id,
        job_name: job_name || `${business_type} em ${location}`,
        business_type,
        location,
        status: 'running',
        started_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (jobError) {
      throw new Error(`Failed to create job: ${jobError.message}`);
    }

    // Process leads asynchronously
    processLeadsAsync(job.id, user.id, business_type, location);

    return new Response(
      JSON.stringify({
        success: true,
        job_id: job.id,
        message: 'Lead generation started',
      }),
      {
        status: 202,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      }
    );

  } catch (error) {
    console.error('Error:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      }
    );
  }
});

// =====================================================
// ASYNC LEAD PROCESSING FUNCTIONS
// =====================================================

async function processLeadsAsync(
  jobId: string,
  userId: string,
  businessType: string,
  location: string
) {
  try {
    // Update progress: Starting Google Maps search
    await updateJobProgress(jobId, 10, 'Searching Google Maps...');

    // Step 1: Search Google Maps
    const mapsResults = await searchGoogleMaps(businessType, location);
    
    if (!mapsResults || mapsResults.length === 0) {
      await updateJobProgress(jobId, 100, 'No results found', 'failed');
      return;
    }

    await updateJobProgress(jobId, 30, `Found ${mapsResults.length} businesses`);

    // Step 2: Enrich data with Instagram and CNPJ
    const enrichedLeads: EnrichedLead[] = [];
    const totalBusinesses = mapsResults.length;

    for (let i = 0; i < mapsResults.length; i++) {
      const business = mapsResults[i];
      const progress = 30 + Math.floor((i / totalBusinesses) * 50);
      
      await updateJobProgress(jobId, progress, `Processing: ${business.title}`);

      try {
        const enrichedData = await enrichBusinessData(business, location);
        enrichedLeads.push(enrichedData);
      } catch (error) {
        console.error(`Error enriching ${business.title}:`, error);
        // Add business without enriched data
        enrichedLeads.push({
          ...business,
          extraction_quality_score: 0.3,
        });
      }

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Step 3: Save leads to database
    await updateJobProgress(jobId, 80, 'Saving leads to database...');

    const leadsToInsert = enrichedLeads.map(lead => ({
      job_id: jobId,
      user_id: userId,
      business_name: lead.title,
      address: lead.address || null,
      phone_maps: lead.phone || null,
      website: lead.website || null,
      rating_maps: lead.rating || null,
      reviews_count: lead.reviews || null,
      instagram_url: lead.instagram_url || null,
      instagram_confidence: lead.instagram_confidence || null,
      cnpj: lead.cnpj || null,
      cnpj_confidence: lead.cnpj_confidence || null,
      extraction_quality_score: lead.extraction_quality_score || 0.5,
    }));

    const { error: insertError } = await supabase
      .from('leads')
      .insert(leadsToInsert);

    if (insertError) {
      throw new Error(`Failed to save leads: ${insertError.message}`);
    }

    // Update job completion
    const stats = {
      total_leads_found: enrichedLeads.length,
      leads_with_instagram: enrichedLeads.filter(l => l.instagram_url).length,
      leads_with_cnpj: enrichedLeads.filter(l => l.cnpj).length,
    };

    await supabase
      .from('lead_jobs')
      .update({
        status: 'completed',
        progress: 100,
        message: `Completed! Found ${stats.total_leads_found} leads`,
        completed_at: new Date().toISOString(),
        ...stats,
      })
      .eq('id', jobId);

  } catch (error) {
    console.error('Error in processLeadsAsync:', error);
    await updateJobProgress(jobId, 100, `Error: ${error.message}`, 'failed');
  }
}

async function updateJobProgress(
  jobId: string,
  progress: number,
  message: string,
  status?: string
) {
  const updateData: any = { progress, message };
  if (status) updateData.status = status;

  await supabase
    .from('lead_jobs')
    .update(updateData)
    .eq('id', jobId);
}

async function searchGoogleMaps(
  businessType: string,
  location: string
): Promise<GoogleMapsResult[]> {
  if (!SERPAPI_KEY) {
    throw new Error('SerpApi key not configured');
  }

  const params = new URLSearchParams({
    api_key: SERPAPI_KEY,
    engine: 'google_maps',
    q: businessType,
    location: `${location}, Brasil`,
    hl: 'pt-br',
    gl: 'br',
  });

  const response = await fetch(`https://serpapi.com/search?${params}`);
  const data = await response.json();

  if (data.error) {
    throw new Error(`SerpApi error: ${data.error}`);
  }

  return (data.local_results || []).map((result: any) => ({
    title: result.title,
    address: result.address,
    phone: result.phone,
    website: result.website,
    rating: result.rating,
    reviews: result.reviews,
  }));
}

async function enrichBusinessData(
  business: GoogleMapsResult,
  location: string
): Promise<EnrichedLead> {
  const city = location.split(',')[0];
  const query = `"${business.title}" "${city}" instagram cnpj`;

  if (!SERPAPI_KEY) {
    return { ...business, extraction_quality_score: 0.3 };
  }

  try {
    const params = new URLSearchParams({
      api_key: SERPAPI_KEY,
      engine: 'google',
      q: query,
      hl: 'pt-br',
      gl: 'br',
      num: '20',
    });

    const response = await fetch(`https://serpapi.com/search?${params}`);
    const data = await response.json();

    if (data.error) {
      console.error('Google search error:', data.error);
      return { ...business, extraction_quality_score: 0.3 };
    }

    const results = data.organic_results || [];
    
    // Extract Instagram URL
    const { url: instagramUrl, confidence: instagramConfidence } = 
      extractInstagramUrl(business.title, city, results);
    
    // Extract CNPJ
    const { cnpj, confidence: cnpjConfidence } = 
      extractCNPJ(business.title, city, results);

    // Calculate overall quality score
    const qualityScore = calculateQualityScore(
      instagramUrl, instagramConfidence,
      cnpj, cnpjConfidence
    );

    return {
      ...business,
      instagram_url: instagramUrl,
      instagram_confidence: instagramConfidence,
      cnpj,
      cnpj_confidence: cnpjConfidence,
      extraction_quality_score: qualityScore,
    };

  } catch (error) {
    console.error('Error enriching business data:', error);
    return { ...business, extraction_quality_score: 0.3 };
  }
}

function extractInstagramUrl(
  businessName: string,
  city: string,
  results: any[]
): { url: string | null; confidence: number } {
  for (const result of results) {
    const link = result.link || '';
    
    if (link.includes('instagram.com/') && 
        !link.includes('/p/') && 
        !link.includes('/reel/')) {
      
      const confidence = calculateRelevanceScore(businessName, city, result);
      
      if (confidence >= 0.3) {
        return {
          url: link.split('?')[0].replace(/\/$/, ''),
          confidence: Math.round(confidence * 100) / 100,
        };
      }
    }
  }
  
  return { url: null, confidence: 0 };
}

function extractCNPJ(
  businessName: string,
  city: string,
  results: any[]
): { cnpj: string | null; confidence: number } {
  const cnpjPattern = /\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/g;
  
  for (const result of results) {
    const text = `${result.title || ''} ${result.snippet || ''}`;
    const matches = text.match(cnpjPattern);
    
    if (matches && matches.length > 0) {
      const confidence = calculateRelevanceScore(businessName, city, result);
      
      if (confidence >= 0.4) {
        return {
          cnpj: matches[0],
          confidence: Math.round(confidence * 100) / 100,
        };
      }
    }
  }
  
  return { cnpj: null, confidence: 0 };
}

function calculateRelevanceScore(
  businessName: string,
  city: string,
  result: any
): number {
  const title = result.title || '';
  const snippet = result.snippet || '';
  const content = `${title} ${snippet}`.toLowerCase();
  
  // Normalize texts
  const normalizedBusiness = normalizeText(businessName);
  const normalizedCity = normalizeText(city);
  const normalizedContent = normalizeText(content);
  
  // Calculate name similarity
  const nameSimilarity = calculateStringSimilarity(normalizedBusiness, title.toLowerCase());
  
  // Check if city is mentioned
  const cityMentioned = normalizedContent.includes(normalizedCity) ? 1 : 0;
  
  // Calculate keyword coverage
  const businessWords = normalizedBusiness.split(' ').filter(w => w.length > 2);
  const wordsFound = businessWords.filter(word => 
    normalizedContent.includes(word)
  ).length;
  const wordCoverage = businessWords.length > 0 ? wordsFound / businessWords.length : 0;
  
  // Weighted score
  return (nameSimilarity * 0.4) + (cityMentioned * 0.3) + (wordCoverage * 0.3);
}

function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove accents
    .replace(/[^a-z0-9\s]/g, '') // Remove special chars
    .replace(/\s+/g, ' ') // Normalize spaces
    .trim();
}

function calculateStringSimilarity(str1: string, str2: string): number {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) return 1.0;
  
  const editDistance = levenshteinDistance(longer, shorter);
  return (longer.length - editDistance) / longer.length;
}

function levenshteinDistance(str1: string, str2: string): number {
  const matrix = Array(str2.length + 1).fill(null).map(() => 
    Array(str1.length + 1).fill(null)
  );
  
  for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
  
  for (let j = 1; j <= str2.length; j++) {
    for (let i = 1; i <= str1.length; i++) {
      const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1, // deletion
        matrix[j - 1][i] + 1, // insertion
        matrix[j - 1][i - 1] + indicator // substitution
      );
    }
  }
  
  return matrix[str2.length][str1.length];
}

function calculateQualityScore(
  instagramUrl: string | null,
  instagramConfidence: number | null,
  cnpj: string | null,
  cnpjConfidence: number | null
): number {
  let score = 0.3; // Base score
  
  if (instagramUrl && instagramConfidence) {
    score += instagramConfidence * 0.3;
  }
  
  if (cnpj && cnpjConfidence) {
    score += cnpjConfidence * 0.4;
  }
  
  return Math.min(Math.round(score * 100) / 100, 1.0);
}
