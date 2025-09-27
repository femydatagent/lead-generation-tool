import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

// =====================================================
// EXPORT LEADS EDGE FUNCTION
// =====================================================

// Initialize Supabase client
const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

Deno.serve(async (req: Request) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
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

    // Extract job ID from URL
    const url = new URL(req.url);
    const jobId = url.pathname.split('/').pop();

    if (!jobId) {
      throw new Error('Job ID is required');
    }

    // Get job details to verify ownership and get job info
    const { data: job, error: jobError } = await supabase
      .from('lead_jobs')
      .select('id, job_name, business_type, location, status')
      .eq('id', jobId)
      .eq('user_id', user.id)
      .single();

    if (jobError || !job) {
      throw new Error('Job not found');
    }

    if (job.status !== 'completed') {
      throw new Error('Job is not completed yet');
    }

    // Get all leads for this job
    const { data: leads, error: leadsError } = await supabase
      .from('leads')
      .select(`
        business_name,
        address,
        phone_maps,
        website,
        rating_maps,
        reviews_count,
        instagram_url,
        instagram_confidence,
        cnpj,
        cnpj_confidence,
        instagram_bio,
        instagram_followers,
        instagram_posts_count,
        instagram_business_email,
        instagram_business_phone,
        cnpj_status,
        company_owners,
        company_email,
        company_phone,
        extraction_quality_score,
        created_at
      `)
      .eq('job_id', jobId)
      .order('extraction_quality_score', { ascending: false });

    if (leadsError) {
      throw new Error(`Failed to fetch leads: ${leadsError.message}`);
    }

    if (!leads || leads.length === 0) {
      throw new Error('No leads found for this job');
    }

    // Generate CSV content
    const csvContent = generateCSV(leads);

    // Generate filename
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `leads_${job.business_type.replace(/\s+/g, '_')}_${job.location.split(',')[0].replace(/\s+/g, '_')}_${timestamp}.csv`;

    return new Response(csvContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Expose-Headers': 'Content-Disposition',
      },
    });

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

function generateCSV(leads: any[]): string {
  // Define CSV headers
  const headers = [
    'Nome da Empresa',
    'Endereço',
    'Telefone (Maps)',
    'Website',
    'Avaliação (Maps)',
    'Número de Avaliações',
    'URL Instagram',
    'Confiança Instagram',
    'CNPJ',
    'Confiança CNPJ',
    'Bio Instagram',
    'Seguidores Instagram',
    'Posts Instagram',
    'Email Instagram',
    'Telefone Instagram',
    'Status CNPJ',
    'Sócios da Empresa',
    'Email Empresarial',
    'Telefone Empresarial',
    'Score de Qualidade',
    'Data de Extração'
  ];

  // Create CSV rows
  const rows = leads.map(lead => [
    escapeCSVField(lead.business_name || ''),
    escapeCSVField(lead.address || ''),
    escapeCSVField(lead.phone_maps || ''),
    escapeCSVField(lead.website || ''),
    lead.rating_maps || '',
    lead.reviews_count || '',
    escapeCSVField(lead.instagram_url || ''),
    lead.instagram_confidence || '',
    escapeCSVField(lead.cnpj || ''),
    lead.cnpj_confidence || '',
    escapeCSVField(lead.instagram_bio || ''),
    lead.instagram_followers || '',
    lead.instagram_posts_count || '',
    escapeCSVField(lead.instagram_business_email || ''),
    escapeCSVField(lead.instagram_business_phone || ''),
    escapeCSVField(lead.cnpj_status || ''),
    escapeCSVField(lead.company_owners || ''),
    escapeCSVField(lead.company_email || ''),
    escapeCSVField(lead.company_phone || ''),
    lead.extraction_quality_score || '',
    lead.created_at ? new Date(lead.created_at).toLocaleDateString('pt-BR') : ''
  ]);

  // Combine headers and rows
  const csvLines = [headers, ...rows];
  
  // Convert to CSV string
  return csvLines.map(row => row.join(',')).join('\n');
}

function escapeCSVField(field: string): string {
  if (!field) return '';
  
  // If field contains comma, newline, or quote, wrap in quotes and escape internal quotes
  if (field.includes(',') || field.includes('\n') || field.includes('"')) {
    return `"${field.replace(/"/g, '""')}"`;
  }
  
  return field;
}
