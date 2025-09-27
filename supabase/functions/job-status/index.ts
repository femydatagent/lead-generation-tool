import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

// =====================================================
// JOB STATUS EDGE FUNCTION
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

    // Get job details
    const { data: job, error: jobError } = await supabase
      .from('lead_jobs')
      .select(`
        id,
        job_name,
        business_type,
        location,
        status,
        progress,
        message,
        total_leads_found,
        leads_with_instagram,
        leads_with_cnpj,
        error_message,
        started_at,
        completed_at,
        created_at,
        updated_at
      `)
      .eq('id', jobId)
      .eq('user_id', user.id)
      .single();

    if (jobError || !job) {
      throw new Error('Job not found');
    }

    // If job is completed, get additional statistics
    let stats = null;
    if (job.status === 'completed') {
      const { data: leadsStats } = await supabase
        .from('leads')
        .select(`
          extraction_quality_score,
          instagram_url,
          cnpj
        `)
        .eq('job_id', jobId);

      if (leadsStats) {
        const totalLeads = leadsStats.length;
        const highQualityLeads = leadsStats.filter(l => 
          (l.extraction_quality_score || 0) >= 0.7
        ).length;
        const avgQualityScore = totalLeads > 0 
          ? leadsStats.reduce((sum, l) => sum + (l.extraction_quality_score || 0), 0) / totalLeads
          : 0;

        stats = {
          total_leads: totalLeads,
          high_quality_leads: highQualityLeads,
          avg_quality_score: Math.round(avgQualityScore * 100) / 100,
          quality_percentage: totalLeads > 0 ? Math.round((highQualityLeads / totalLeads) * 100) : 0,
        };
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        job: {
          ...job,
          stats,
        },
      }),
      {
        status: 200,
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
