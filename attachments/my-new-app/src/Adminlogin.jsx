import React, { useState } from 'react';
import {
    ShieldCheck, Lock, UserRound, Eye, EyeOff,
    Globe, ChevronDown, ArrowLeft, Activity,
    LayoutDashboard, Loader2, ShieldAlert, CheckCircle2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- CONFIGURATION ---
const ADMIN_DASHBOARD_ROUTE = "/admin-dashboard";
const HOME_ROUTE = "/";

// Mock Developer-Provisioned Credentials (For Demo)
const MOCK_ADMIN_ID = "Admin2026";
const MOCK_ADMIN_PASS = "2026password";

// --- THEME COLORS ---
const COLORS = {
    deepIndigo: '#1E2A5A',
    richTeal: '#0F766E',
    softAqua: '#CFF7F2',
    softIvory: '#F8F7F4',
    pureWhite: '#FFFFFF',
    charcoalNavy: '#172033',
    slateGray: '#667085',
    softGray: '#E6E8EE',
};

// --- COMPONENTS ---

const LanguageSelector = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [lang, setLang] = useState('English');
    const languages = ['English', 'తెలుగు', 'हिंदी', 'मराठी'];

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#E6E8EE] rounded-lg hover:bg-gray-50 transition-all"
            >
                <Globe size={18} className="text-[#0F766E]" />
                <span className="font-medium text-[#1E2A5A] text-sm">{lang}</span>
                <ChevronDown size={14} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
                        className="absolute right-0 mt-2 w-36 bg-white border border-[#E6E8EE] rounded-xl shadow-xl z-50 overflow-hidden"
                    >
                        {languages.map((l) => (
                            <button key={l} onClick={() => { setLang(l); setIsOpen(false); }}
                                className="w-full text-left px-4 py-2.5 hover:bg-[#CFF7F2] transition-colors text-sm text-[#172033]"
                            >
                                {l}
                            </button>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const AdminIllustration = () => (
    <div className="relative w-full max-w-sm aspect-square flex items-center justify-center mt-10">
        {/* Abstract Data/Network Rings */}
        <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 border-2 border-dashed border-[#0F766E]/20 rounded-full"
        />
        <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
            className="absolute inset-8 border border-dashed border-[#1E2A5A]/10 rounded-full"
        />

        {/* Central Admin Hub */}
        <div className="w-24 h-24 bg-white rounded-[2rem] shadow-2xl flex items-center justify-center z-10 border border-[#E6E8EE]">
            <LayoutDashboard size={48} className="text-[#1E2A5A]" />
        </div>

        {/* Connected Nodes */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 p-3 bg-[#CFF7F2] rounded-xl shadow-lg border border-white text-[#0F766E]">
            <Activity size={24} />
        </div>
        <div className="absolute bottom-10 right-0 p-3 bg-[#1E2A5A] rounded-xl shadow-lg text-white">
            <ShieldCheck size={24} />
        </div>
        <div className="absolute bottom-10 left-0 p-3 bg-white rounded-xl shadow-lg border border-[#E6E8EE] text-[#1E2A5A]">
            <UserRound size={24} />
        </div>
    </div>
);

export default function AdminLogin() {
    const [adminId, setAdminId] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        if (!adminId) return setError('Please enter your Admin Login ID.');
        if (!password) return setError('Please enter your password.');

        setIsLoading(true);

        // Simulated Authentication Logic
        setTimeout(() => {
            if (adminId === MOCK_ADMIN_ID && password === MOCK_ADMIN_PASS) {
                window.location.href = ADMIN_DASHBOARD_ROUTE;
            } else {
                setError('Invalid Admin Login ID or password. Please try again.');
                setIsLoading(false);
            }
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-[#F8F7F4] font-sans text-[#172033] flex flex-col overflow-x-hidden">

            {/* PROFESSIONAL HEADER */}
            <nav className="h-20 px-8 md:px-16 flex items-center justify-between border-b border-[#E6E8EE] bg-white/50 backdrop-blur-md sticky top-0 z-40">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[#1E2A5A] rounded-xl flex items-center justify-center text-white shadow-lg">
                        <ShieldCheck size={24} />
                    </div>
                    <div>
                        <h1 className="text-xl font-black text-[#1E2A5A] tracking-tight uppercase leading-none">Aarogya</h1>
                        <p className="text-[10px] font-bold text-[#0F766E] tracking-[0.2em] uppercase">Connect</p>
                    </div>
                </div>

                <div className="flex items-center gap-4 md:gap-8">
                    <LanguageSelector />
                    <a href={HOME_ROUTE} className="text-sm font-bold text-[#667085] hover:text-[#1E2A5A] flex items-center gap-2 transition-colors group">
                        <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
                        <span className="hidden sm:inline">Back to Home</span>
                    </a>
                </div>
            </nav>

            {/* MAIN CONTENT AREA */}
            <div className="flex-1 flex flex-col lg:flex-row items-center justify-center px-6 py-12 gap-16 lg:gap-32 max-w-7xl mx-auto w-full">

                {/* LEFT COLUMN: INTRO & VISUAL */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    className="flex-1 text-center lg:text-left flex flex-col items-center lg:items-start"
                >
                    <span className="px-4 py-1.5 bg-[#CFF7F2] text-[#0F766E] text-[10px] font-black uppercase tracking-widest rounded-full border border-[#0F766E]/10">
                        Authorized Administrative Access
                    </span>
                    <h2 className="text-5xl lg:text-6xl font-black text-[#1E2A5A] mt-6 leading-[1.1]">
                        Admin Portal
                    </h2>
                    <p className="text-xl lg:text-2xl font-bold text-[#172033] mt-4 opacity-80">
                        Secure access to healthcare administration.
                    </p>
                    <p className="text-[#667085] mt-6 text-lg leading-relaxed max-w-lg">
                        AarogyaConnect provides authorized administrators with a centralized entry point for managing the healthcare platform, services and connected operations.
                    </p>

                    <AdminIllustration />
                </motion.div>

                {/* RIGHT COLUMN: LOGIN CARD */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="w-full max-w-md"
                >
                    <div className="bg-white rounded-[2.5rem] border border-[#E6E8EE] shadow-2xl shadow-indigo-900/5 p-10 md:p-12 relative">

                        {/* Login Card Header */}
                        <div className="mb-10 text-center lg:text-left">
                            <div className="flex items-center justify-center lg:justify-start gap-2 mb-4">
                                <CheckCircle2 size={16} className="text-[#0F766E]" />
                                <span className="text-[11px] font-black text-[#667085] uppercase tracking-widest">
                                    Secure Gateway
                                </span>
                            </div>
                            <h3 className="text-3xl font-black text-[#1E2A5A]">Admin Login</h3>
                            <p className="text-sm text-[#667085] mt-2 leading-relaxed">
                                Sign in using the credentials provided by the system developer.
                            </p>
                        </div>

                        <form onSubmit={handleLogin} className="space-y-6">

                            {/* ADMIN ID INPUT */}
                            <div className="space-y-2">
                                <label className="text-xs font-black text-[#1E2A5A] uppercase tracking-wider ml-1">
                                    Admin Login ID
                                </label>
                                <div className="relative group">
                                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#667085] group-focus-within:text-[#0F766E] transition-colors">
                                        <UserRound size={20} />
                                    </div>
                                    <input
                                        type="text"
                                        value={adminId}
                                        onChange={(e) => setAdminId(e.target.value)}
                                        placeholder="Enter Admin Login ID"
                                        className="w-full pl-12 pr-4 py-4 bg-white border border-[#E6E8EE] rounded-2xl text-[#172033] focus:outline-none focus:ring-4 focus:ring-[#0F766E]/5 focus:border-[#0F766E] transition-all placeholder:text-gray-300 font-medium"
                                    />
                                </div>
                            </div>

                            {/* PASSWORD INPUT */}
                            <div className="space-y-2">
                                <label className="text-xs font-black text-[#1E2A5A] uppercase tracking-wider ml-1">
                                    Password
                                </label>
                                <div className="relative group">
                                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#667085] group-focus-within:text-[#0F766E] transition-colors">
                                        <Lock size={20} />
                                    </div>
                                    <input
                                        type={showPassword ? "text" : "password"}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="Enter password"
                                        className="w-full pl-12 pr-14 py-4 bg-white border border-[#E6E8EE] rounded-2xl text-[#172033] focus:outline-none focus:ring-4 focus:ring-[#0F766E]/5 focus:border-[#0F766E] transition-all placeholder:text-gray-300 font-medium"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-4 top-1/2 -translate-y-1/2 text-[#667085] hover:text-[#1E2A5A] transition-colors focus:outline-none"
                                        title={showPassword ? "Hide password" : "Show password"}
                                    >
                                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                    </button>
                                </div>
                            </div>

                            {/* ERROR STATE */}
                            <AnimatePresence>
                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="flex items-center gap-3 text-red-600 bg-red-50 p-4 rounded-2xl border border-red-100 shadow-sm"
                                    >
                                        <ShieldAlert size={20} className="shrink-0" />
                                        <span className="text-xs font-bold leading-tight">{error}</span>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* LOGIN BUTTON */}
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-4 bg-[#0F766E] text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-[#0d665f] active:scale-[0.98] transition-all shadow-xl shadow-teal-900/10 flex items-center justify-center gap-3 disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 size={20} className="animate-spin" />
                                        <span>Signing In...</span>
                                    </>
                                ) : (
                                    <>
                                        <span>Login</span>
                                        <LayoutDashboard size={18} />
                                    </>
                                )}
                            </button>
                        </form>

                        {/* SECURITY FOOTER */}
                        <div className="mt-10 pt-8 border-t border-[#E6E8EE] flex flex-col items-center gap-3">
                            <div className="flex items-center gap-2 text-[#0F766E]">
                                <ShieldCheck size={14} />
                                <span className="text-[10px] font-black uppercase tracking-widest">
                                    Authorized Admin Access Only
                                </span>
                            </div>
                            <p className="text-[9px] text-[#667085] text-center leading-relaxed max-w-[200px]">
                                Authentication attempts are logged. Unauthorized access is prohibited.
                            </p>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* FOOTER */}
            <footer className="py-8 text-center text-[10px] font-black text-[#667085] uppercase tracking-[0.3em] opacity-40">
                AarogyaConnect Healthcare Administration Gateway • 2026
            </footer>
        </div>
    );
}