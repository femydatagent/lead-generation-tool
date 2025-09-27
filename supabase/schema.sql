-- =====================================================
-- LEAD GENERATION TOOL - SUPABASE BACKEND SCHEMA
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- PROFILES TABLE (extends auth.users)
-- =====================================================
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    api_credits INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- API KEYS TABLE (for user's external API keys)
-- =====================================================
CREATE TABLE public.api_keys (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    service_name TEXT NOT NULL CHECK (service_name IN ('serpapi', 'datastone', 'apify')),
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, service_name)
);

-- =====================================================
-- LEAD JOBS TABLE (tracks lead generation jobs)
-- =====================================================
CREATE TABLE public.lead_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    job_name TEXT NOT NULL,
    business_type TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    message TEXT DEFAULT 'Job created',
    total_leads_found INTEGER DEFAULT 0,
    leads_with_instagram INTEGER DEFAULT 0,
    leads_with_cnpj INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- LEADS TABLE (stores individual lead results)
-- =====================================================
CREATE TABLE public.leads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_id UUID REFERENCES public.lead_jobs(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    
    -- Basic info from Google Maps
    business_name TEXT NOT NULL,
    address TEXT,
    phone_maps TEXT,
    website TEXT,
    rating_maps DECIMAL(2,1),
    reviews_count INTEGER,
    
    -- Enriched data
    instagram_url TEXT,
    instagram_confidence DECIMAL(3,2),
    cnpj TEXT,
    cnpj_confidence DECIMAL(3,2),
    
    -- Instagram data (from Apify)
    instagram_bio TEXT,
    instagram_followers INTEGER,
    instagram_posts_count INTEGER,
    instagram_business_email TEXT,
    instagram_business_phone TEXT,
    instagram_photos_urls TEXT[], -- Array of photo URLs
    
    -- CNPJ data (from DataStone)
    cnpj_status TEXT,
    company_owners TEXT,
    company_email TEXT,
    company_phone TEXT,
    
    -- Metadata
    extraction_quality_score DECIMAL(3,2), -- Overall quality score
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- USAGE LOGS TABLE (tracks API usage for billing)
-- =====================================================
CREATE TABLE public.usage_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    job_id UUID REFERENCES public.lead_jobs(id) ON DELETE SET NULL,
    service_name TEXT NOT NULL CHECK (service_name IN ('serpapi', 'datastone', 'apify')),
    api_calls_count INTEGER DEFAULT 1,
    credits_used INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES for better performance
-- =====================================================
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_api_keys_user_service ON public.api_keys(user_id, service_name);
CREATE INDEX idx_lead_jobs_user_status ON public.lead_jobs(user_id, status);
CREATE INDEX idx_lead_jobs_created_at ON public.lead_jobs(created_at DESC);
CREATE INDEX idx_leads_job_id ON public.leads(job_id);
CREATE INDEX idx_leads_user_id ON public.leads(user_id);
CREATE INDEX idx_leads_business_name ON public.leads(business_name);
CREATE INDEX idx_usage_logs_user_date ON public.usage_logs(user_id, created_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lead_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_logs ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- API Keys policies
CREATE POLICY "Users can manage own API keys" ON public.api_keys
    FOR ALL USING (auth.uid() = user_id);

-- Lead Jobs policies
CREATE POLICY "Users can view own jobs" ON public.lead_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own jobs" ON public.lead_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own jobs" ON public.lead_jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own jobs" ON public.lead_jobs
    FOR DELETE USING (auth.uid() = user_id);

-- Leads policies
CREATE POLICY "Users can view own leads" ON public.leads
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own leads" ON public.leads
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own leads" ON public.leads
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own leads" ON public.leads
    FOR DELETE USING (auth.uid() = user_id);

-- Usage Logs policies
CREATE POLICY "Users can view own usage" ON public.usage_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can insert usage logs" ON public.usage_logs
    FOR INSERT WITH CHECK (true); -- Allow system to insert

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON public.api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lead_jobs_updated_at BEFORE UPDATE ON public.lead_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON public.leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Trigger to create profile on signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to encrypt API keys
CREATE OR REPLACE FUNCTION encrypt_api_key(api_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(api_key, gen_salt('bf'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to decrypt API keys (for system use)
CREATE OR REPLACE FUNCTION decrypt_api_key(encrypted_key TEXT, plain_key TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN encrypted_key = crypt(plain_key, encrypted_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate job statistics
CREATE OR REPLACE FUNCTION calculate_job_stats(job_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_leads', COUNT(*),
        'with_instagram', COUNT(*) FILTER (WHERE instagram_url IS NOT NULL),
        'with_cnpj', COUNT(*) FILTER (WHERE cnpj IS NOT NULL),
        'avg_quality_score', ROUND(AVG(extraction_quality_score), 2),
        'high_quality_leads', COUNT(*) FILTER (WHERE extraction_quality_score >= 0.7)
    )
    INTO result
    FROM public.leads
    WHERE job_id = job_uuid;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update job progress
CREATE OR REPLACE FUNCTION update_job_progress(
    job_uuid UUID,
    new_progress INTEGER,
    new_message TEXT DEFAULT NULL,
    new_status TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE public.lead_jobs
    SET 
        progress = new_progress,
        message = COALESCE(new_message, message),
        status = COALESCE(new_status, status),
        updated_at = NOW()
    WHERE id = job_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- VIEWS FOR ANALYTICS
-- =====================================================

-- View for user dashboard statistics
CREATE VIEW public.user_dashboard_stats AS
SELECT 
    p.id as user_id,
    p.email,
    p.plan,
    p.api_credits,
    COUNT(DISTINCT lj.id) as total_jobs,
    COUNT(DISTINCT lj.id) FILTER (WHERE lj.status = 'completed') as completed_jobs,
    COUNT(DISTINCT l.id) as total_leads,
    COUNT(DISTINCT l.id) FILTER (WHERE l.instagram_url IS NOT NULL) as leads_with_instagram,
    COUNT(DISTINCT l.id) FILTER (WHERE l.cnpj IS NOT NULL) as leads_with_cnpj,
    SUM(ul.credits_used) as total_credits_used
FROM public.profiles p
LEFT JOIN public.lead_jobs lj ON p.id = lj.user_id
LEFT JOIN public.leads l ON p.id = l.user_id
LEFT JOIN public.usage_logs ul ON p.id = ul.user_id
GROUP BY p.id, p.email, p.plan, p.api_credits;

-- View for recent activity
CREATE VIEW public.recent_activity AS
SELECT 
    'job_created' as activity_type,
    lj.id as reference_id,
    lj.user_id,
    lj.job_name as description,
    lj.created_at as activity_date
FROM public.lead_jobs lj
UNION ALL
SELECT 
    'job_completed' as activity_type,
    lj.id as reference_id,
    lj.user_id,
    CONCAT('Completed: ', lj.job_name, ' (', lj.total_leads_found, ' leads)') as description,
    lj.completed_at as activity_date
FROM public.lead_jobs lj
WHERE lj.status = 'completed' AND lj.completed_at IS NOT NULL
ORDER BY activity_date DESC;

-- =====================================================
-- SAMPLE DATA (for testing)
-- =====================================================

-- This will be populated when users sign up and use the system
-- No sample data needed for production

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon;

-- Grant permissions on tables
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- Grant execute on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon;
