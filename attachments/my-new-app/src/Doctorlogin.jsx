import React, { useState } from 'react';
import {
    Stethoscope, Lock, UserRound, Eye, EyeOff,
    ShieldCheck, Globe, ChevronDown, ArrowLeft,
    Activity, HeartPulse, ShieldAlert, Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- CONFIGURATION ---
const DOCTOR_DASHBOARD_ROUTE = "/doctor-dashboard";
const HOME_ROUTE = "/";

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
                className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#E6E8EE] rounded-lg hover:bg-gray-50 transition-colors"
            >
                <Globe size={18} className="text-[#0F766E]" />
                <span className="font-medium text-[#1E2A5A] text-sm">{lang}</span>
                <ChevronDown size={14} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
                        className="absolute right-0 mt-2 w-32 bg-white border border-[#E6E8EE] rounded-xl shadow-xl z-50 overflow-hidden"
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

const HealthcareNetworkVisual = () => (
    <div className="relative w-full max-w-sm h-64 mt-12 flex items-center justify-center">
        {/* Central Node */}
        <div className="w-20 h-20 bg-white rounded-2xl shadow-xl flex items-center justify-center z-10 border border-[#E6E8EE]">
            <HeartPulse size={40} className="text-[#0F766E]" />
        </div>

        {/* Connections & Secondary Nodes */}
        <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
            className="absolute w-full h-full border-2 border-dashed border-[#0F766E]/20 rounded-full"
        />

        {[
            { icon: UserRound, pos: 'top-0 left-1/2 -translate-x-1/2' },
            { icon: Stethoscope, pos: 'bottom-0 left-1/2 -translate-x-1/2' },
            { icon: Activity, pos: 'left-0 top-1/2 -translate-y-1/2' },
            { icon: ShieldCheck, pos: 'right-0 top-1/2 -translate-y-1/2' }
        ].map((node, i) => (
            <div key={i} className={`absolute ${node.pos} w-12 h-12 bg-[#CFF7F2] rounded-xl flex items-center justify-center text-[#1E2A5A] shadow-lg`}>
                <node.icon size={20} />
            </div>
        ))}
    </div>
);

export default function DoctorLogin() {
    const [doctorId, setDoctorId] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        if (!doctorId) return setError('Please enter your Doctor ID.');
        if (!password) return setError('Please enter your password.');

        setLoading(true);

        // Simulate authentication
        setTimeout(() => {
            setLoading(false);
            // Example validation logic
            if (doctorId === 'DOC123' && password === 'password') {
                window.location.href = DOCTOR_DASHBOARD_ROUTE;
            } else {
                setError('Invalid Doctor ID or password. Please try again.');
            }
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-[#F8F7F4] font-sans text-[#172033] flex flex-col">

            {/* TOP NAVIGATION */}
            <nav className="h-20 px-8 md:px-12 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-[#1E2A5A] rounded-xl flex items-center justify-center text-white shadow-lg">
                        <Activity size={24} />
                    </div>
                    <div className="hidden sm:block">
                        <h1 className="text-xl font-black text-[#1E2A5A] tracking-tight uppercase leading-none">Aarogya</h1>
                        <p className="text-[10px] font-bold text-[#0F766E] tracking-[0.2em] uppercase">Connect</p>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <LanguageSelector />
                    <a href={HOME_ROUTE} className="text-sm font-bold text-[#667085] hover:text-[#1E2A5A] flex items-center gap-2 transition-colors">
                        <ArrowLeft size={16} /> Back to Home
                    </a>
                </div>
            </nav>

            {/* MAIN CONTENT CONTAINER */}
            <div className="flex-1 flex flex-col lg:flex-row items-center justify-center px-6 py-12 gap-16 lg:gap-24 max-w-7xl mx-auto w-full">

                {/* LEFT COLUMN: BRANDING & VISUAL */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex-1 text-center lg:text-left max-w-lg"
                >
                    <span className="px-4 py-1.5 bg-[#CFF7F2] text-[#0F766E] text-xs font-black uppercase tracking-widest rounded-full">
                        Authorized Personnel Only
                    </span>
                    <h2 className="text-5xl font-black text-[#1E2A5A] mt-6 leading-tight">
                        Doctor Portal
                    </h2>
                    <p className="text-xl font-bold text-[#172033] mt-4 opacity-90">
                        Secure access to connected healthcare services.
                    </p>
                    <p className="text-[#667085] mt-6 text-lg leading-relaxed">
                        AarogyaConnect helps healthcare professionals securely connect with patients, healthcare centres and specialist services through one coordinated digital platform.
                    </p>

                    <div className="hidden lg:flex justify-start">
                        <HealthcareNetworkVisual />
                    </div>
                </motion.div>

                {/* RIGHT COLUMN: LOGIN CARD */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="w-full max-w-md"
                >
                    <div className="bg-white rounded-[2rem] border border-[#E6E8EE] shadow-2xl shadow-indigo-900/5 p-10 relative overflow-hidden">

                        {/* Security Background Accent */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-[#CFF7F2]/30 rounded-full -mr-16 -mt-16 blur-3xl pointer-events-none" />

                        <div className="relative">
                            <div className="mb-10">
                                <span className="text-[10px] font-black text-[#667085] uppercase tracking-[0.2em] block mb-2">
                                    Authorized Access
                                </span>
                                <h3 className="text-3xl font-black text-[#1E2A5A]">Doctor Login</h3>
                                <p className="text-sm text-[#667085] mt-2">
                                    Sign in using your authorized credentials.
                                </p>
                            </div>

                            <form onSubmit={handleLogin} className="space-y-6">

                                {/* DOCTOR ID INPUT */}
                                <div className="space-y-2">
                                    <label className="text-sm font-bold text-[#1E2A5A] ml-1">Doctor ID</label>
                                    <div className="relative group">
                                        <UserRound className="absolute left-4 top-1/2 -translate-y-1/2 text-[#667085] group-focus-within:text-[#0F766E] transition-colors" size={20} />
                                        <input
                                            type="text"
                                            value={doctorId}
                                            onChange={(e) => setDoctorId(e.target.value)}
                                            placeholder="Enter your Doctor ID"
                                            className="w-full pl-12 pr-4 py-4 bg-white border border-[#E6E8EE] rounded-2xl text-[#172033] focus:outline-none focus:ring-2 focus:ring-[#0F766E]/20 focus:border-[#0F766E] transition-all placeholder:text-gray-300"
                                        />
                                    </div>
                                </div>

                                {/* PASSWORD INPUT */}
                                <div className="space-y-2">
                                    <div className="flex justify-between items-center px-1">
                                        <label className="text-sm font-bold text-[#1E2A5A]">Password</label>
                                        <button type="button" className="text-xs font-bold text-[#0F766E] hover:underline">Forgot Password?</button>
                                    </div>
                                    <div className="relative group">
                                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-[#667085] group-focus-within:text-[#0F766E] transition-colors" size={20} />
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Enter your password"
                                            className="w-full pl-12 pr-12 py-4 bg-white border border-[#E6E8EE] rounded-2xl text-[#172033] focus:outline-none focus:ring-2 focus:ring-[#0F766E]/20 focus:border-[#0F766E] transition-all placeholder:text-gray-300"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-4 top-1/2 -translate-y-1/2 text-[#667085] hover:text-[#1E2A5A] transition-colors"
                                        >
                                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </button>
                                    </div>
                                </div>

                                {/* ERROR MESSAGE */}
                                <AnimatePresence>
                                    {error && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-xl border border-red-100"
                                        >
                                            <ShieldAlert size={18} />
                                            <span className="text-xs font-bold">{error}</span>
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                {/* LOGIN BUTTON */}
                                <button
                                    disabled={loading}
                                    className="w-full py-4 bg-[#0F766E] text-white rounded-2xl font-bold hover:bg-[#0d665f] active:scale-[0.98] transition-all shadow-xl shadow-teal-900/10 flex items-center justify-center gap-3 disabled:opacity-70"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 size={20} className="animate-spin" />
                                            Authenticating...
                                        </>
                                    ) : (
                                        'Login'
                                    )}
                                </button>
                            </form>

                            {/* SECURITY NOTICE */}
                            <div className="mt-10 pt-8 border-t border-[#E6E8EE] flex items-center justify-center gap-2 text-[#667085]">
                                <ShieldCheck size={16} className="text-[#0F766E]" />
                                <span className="text-[10px] font-bold uppercase tracking-wider">
                                    Authorized Healthcare Professional Access
                                </span>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* FOOTER AREA */}
            <footer className="py-8 px-12 text-center text-[10px] font-bold text-[#667085] uppercase tracking-widest opacity-60">
                © 2026 AarogyaConnect • Ministry of Health & Family Welfare Support
            </footer>
        </div>
    );
}