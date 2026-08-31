import React, { useState } from 'react';
import './PatientLogin.css';
import {
    Plus, Hospital, Stethoscope, Activity, ClipboardList, Pill,
    Users, UserCog, Building2, Clock, ShieldCheck, Mail, Lock,
    Eye, EyeOff, ArrowRight, Smartphone, Globe
} from 'lucide-react';

const translations = {
    en: {
        heroBadge: 'Smart Digital Healthcare',
        heroHeading1: 'Healthcare.', heroHeading2: 'Connected.', heroHeading3: 'Simplified.',
        heroDescription: 'One secure platform connecting patients with doctors, healthcare services, appointments, medical records and essential health resources.',
        welcomeText: 'Welcome', welcomeBack: 'Back', welcomeDescription: 'Sign in securely to access your healthcare services.',
        passwordLogin: 'Password Login', mobileOTP: 'Mobile Number Login',
        emailLabel: 'Email ID', emailPlaceholder: 'Enter your email ID',
        mobileLabel: 'Mobile Number', mobilePlaceholder: 'Enter your mobile number',
        passwordLabel: 'Password', passwordPlaceholder: 'Enter your password',
        rememberMe: 'Remember me', forgotPassword: 'Forgot Password?', signIn: 'Sign In',
        newToAarogya: 'New to AarogyaConnect?', createAccount: 'Create Account',
        securityMessage: 'Your health information is securely protected.'
    },
    hi: {
        heroBadge: 'स्मार्ट डिजिटल हेल्थकेयर',
        heroHeading1: 'स्वास्थ्य।', heroHeading2: 'जुड़ा हुआ।', heroHeading3: 'सरल।',
        heroDescription: 'एक सुरक्षित प्लेटफॉर्म जो रोगियों को डॉक्टरों, स्वास्थ्य सेवाओं, अपॉइंटमेंट, मेडिकल रिकॉर्ड और आवश्यक स्वास्थ्य संसाधनों से जोड़ता है।',
        welcomeText: 'स्वागत', welcomeBack: 'है', welcomeDescription: 'अपनी स्वास्थ्य सेवाओं तक सुरक्षित रूप से पहुँचें।',
        passwordLogin: 'पासवर्ड लॉगिन', mobileOTP: 'मोबाइल नंबर लॉगिन',
        emailLabel: 'ईमेल आईडी', emailPlaceholder: 'अपनी ईमेल आईडी दर्ज करें',
        mobileLabel: 'मोबाइल नंबर', mobilePlaceholder: 'अपना मोबाइल नंबर दर्ज करें',
        passwordLabel: 'पासवर्ड', passwordPlaceholder: 'अपना पासवर्ड दर्ज करें',
        rememberMe: 'मुझे याद रखें', forgotPassword: 'पासवर्ड भूल गए?', signIn: 'साइन इन',
        newToAarogya: 'AarogyaConnect में नए हैं?', createAccount: 'अकाउंट बनाएं',
        securityMessage: 'आपकी स्वास्थ्य जानकारी सुरक्षित रूप से संरक्षित है।'
    },
    te: {
        heroBadge: 'స్మార్ట్ డిజిటల్ హెల్త్‌కేర్',
        heroHeading1: 'ఆరోగ్యం.', heroHeading2: 'అనుసంధానించబడింది.', heroHeading3: 'సులభతరంగా.',
        heroDescription: 'రోగులను వైద్యులు, ఆరోగ్య సేవలు, అపాయింట్‌మెంట్లు, మెడికల్ రికార్డులు మరియు ముఖ్యమైన ఆరోగ్య వనరులతో కలిపే సురక్షిత ప్లాట్‌ఫారమ్.',
        welcomeText: 'స్వాగతం', welcomeBack: 'మీకు', welcomeDescription: 'మీ ఆరోగ్య సేవలను సురక్షితంగా ప్రవేశించండి.',
        passwordLogin: 'పాస్వర్డ్ లాగిన్', mobileOTP: 'మొబైల్ నంబర్ లాగిన్',
        emailLabel: 'ఇమెయిల్ ఐడీ', emailPlaceholder: 'మీ ఇమెయిల్ ఐడీ నమోదు చేయండి',
        mobileLabel: 'మొబైల్ నంబర్', mobilePlaceholder: 'మీ మొబైల్ నంబర్ నమోదు చేయండి',
        passwordLabel: 'పాస్వర్డ్', passwordPlaceholder: 'మీ పాస్వర్డ్ నమోదు చేయండి',
        rememberMe: 'నన్ను గుర్తుంచుకో', forgotPassword: 'పాస్వర్డ్ మరిచిపోయారా?', signIn: 'సైన్ ఇన్',
        newToAarogya: 'AarogyaConnect కు కొత్తారా?', createAccount: 'ఖాతా సృష్టించండి',
        securityMessage: 'మీ ఆరోగ్య సమాచారం సురక్షితంగా రక్షించబడుతుంది.'
    },
    mr: {
        heroBadge: 'स्मार्ट डिजिटल हेल्थकेअर',
        heroHeading1: 'आरोग्य.', heroHeading2: 'जोडलेले.', heroHeading3: 'सोपे.',
        heroDescription: 'रुग्णांना डॉक्टर, आरोग्य सेवा, अपॉइंटमेंट, मेडिकल रेकॉर्ड आणि आवश्यक आरोग्य संसाधनांशी जोडणारा सुरक्षित प्लॅटफॉर्म.',
        welcomeText: 'स्वागत', welcomeBack: 'असाल', welcomeDescription: 'तुमच्या आरोग्य सेवांमध्ये सुरक्षितपणे साइन इन करा.',
        passwordLogin: 'पासवर्ड लॉगिन', mobileOTP: 'मोबाइल नंबर लॉगिन',
        emailLabel: 'ईमेल आयडी', emailPlaceholder: 'तुमचा ईमेल आयडी प्रविष्ट करा',
        mobileLabel: 'मोबाइल नंबर', mobilePlaceholder: 'तुमचा मोबाइल नंबर प्रविष्ट करा',
        passwordLabel: 'पासवर्ड', passwordPlaceholder: 'तुमचा पासवर्ड प्रविष्ट करा',
        rememberMe: 'मला लक्षात ठेवा', forgotPassword: 'पासवर्ड विसरलात?', signIn: 'साइन इन',
        newToAarogya: 'AarogyaConnect मध्ये नवीन आहात?', createAccount: 'खाते तयार करा',
        securityMessage: 'तुमची आरोग्य माहिती सुरक्षितपणे संरक्षित आहे.'
    }
};

const PatientLogin = () => {
    const [lang, setLang] = useState('en');
    const [loginMethod, setLoginMethod] = useState('email'); // 'email' or 'mobile'
    const [showPassword, setShowPassword] = useState(false);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const t = translations[lang];
    const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/patient/login/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    username: username,
                    password: password,
                }),
            }
        );

        const data = await response.json();

        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            setError(data.message || "Login failed");
        }

    } catch (err) {
        setError("Unable to connect to the server");
    } finally {
        setLoading(false);
    }
};

    return (
        <div className="patient-login-wrapper antialiased min-h-screen flex flex-col lg:flex-row">

            {/* LEFT SIDE: Content & Visuals */}
            <div className="lg:w-1/2 w-full p-8 lg:p-16 flex flex-col justify-between relative overflow-hidden">
                <div className="relative z-20">
                    <div className="flex items-center gap-2 mb-10 animate-fade-up">
                        <div className="bg-[#1E2A5A] p-2.5 rounded-xl shadow-lg">
                            <Plus className="text-[#CFF7F2] w-6 h-6" />
                        </div>
                        <span className="text-2xl font-extrabold tracking-tight text-[#1E2A5A]">AarogyaConnect</span>
                    </div>

                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-[#E6E8EE] text-[#0F766E] text-xs font-bold tracking-wider uppercase mb-8 animate-fade-up delay-150 shadow-sm">
                        <span className="w-2 h-2 rounded-full bg-[#0F766E] animate-pulse"></span>
                        <span>{t.heroBadge}</span>
                    </div>

                    <h1 className="hero-title font-extrabold mb-8 animate-fade-up delay-300">
                        <span className="text-[#1E2A5A]">{t.heroHeading1}</span>
                        <span className="text-[#0F766E]">{t.heroHeading2}</span>
                        <span className="text-[#1E2A5A]">{t.heroHeading3}</span>
                    </h1>

                    <p className="text-[#667085] text-lg max-w-md leading-relaxed animate-fade-up delay-500">
                        {t.heroDescription}
                    </p>
                </div>

                {/* Isometric Visual - Hidden on mobile to prevent overlap */}
                <div className="hidden lg:flex relative justify-center items-center py-24 animate-scale-in delay-700">
                    <div className="relative iso-card bg-white p-10 rounded-[32px] border border-[#E6E8EE] w-72 h-80 flex flex-col items-center justify-center gap-6">
                        <div className="w-24 h-24 bg-[#CFF7F2] rounded-3xl flex items-center justify-center shadow-inner">
                            <Hospital className="w-12 h-12 text-[#0F766E]" />
                        </div>
                        <div className="w-full space-y-4">
                            <div className="h-2 w-full bg-[#F8F7F4] rounded-full"></div>
                            <div className="h-2 w-2/3 bg-[#F8F7F4] rounded-full"></div>
                            <div className="h-10 w-full bg-[#1E2A5A] rounded-xl mt-4 opacity-10"></div>
                        </div>

                        <div className="absolute -top-12 -left-12 floating"><div className="bg-white p-4 rounded-2xl shadow-lg border border-[#E6E8EE]"><Stethoscope className="w-7 h-7 text-[#1E2A5A]" /></div></div>
                        <div className="absolute top-1/2 -right-16 floating" style={{ animationDelay: '1.5s' }}><div className="bg-white p-5 rounded-2xl shadow-lg border border-[#E6E8EE]"><Activity className="w-8 h-8 text-[#0F766E]" /></div></div>
                        <div className="absolute -bottom-10 left-1/4 floating" style={{ animationDelay: '0.8s' }}><div className="bg-white p-4 rounded-2xl shadow-lg border border-[#E6E8EE]"><ClipboardList className="w-7 h-7 text-[#0F766E]" /></div></div>
                    </div>
                </div>

                {/* Stats */}
                <div className="flex flex-wrap items-center gap-8 lg:gap-12 pt-10 border-t border-[#E6E8EE] animate-fade-up delay-900">
                    <div className="flex items-center gap-3">
                        <Users className="w-5 h-5 text-[#0F766E]" />
                        <div><div className="text-xl font-bold text-[#1E2A5A]">10K+</div><div className="text-[10px] font-bold text-[#667085] uppercase tracking-widest">Patients</div></div>
                    </div>
                    <div className="flex items-center gap-3">
                        <UserCog className="w-5 h-5 text-[#0F766E]" />
                        <div><div className="text-xl font-bold text-[#1E2A5A]">500+</div><div className="text-[10px] font-bold text-[#667085] uppercase tracking-widest">Doctors</div></div>
                    </div>
                    <div className="flex items-center gap-3">
                        <Building2 className="w-5 h-5 text-[#0F766E]" />
                        <div><div className="text-xl font-bold text-[#1E2A5A]">100+</div><div className="text-[10px] font-bold text-[#667085] uppercase tracking-widest">Centers</div></div>
                    </div>
                </div>
            </div>

            {/* RIGHT SIDE: Login Card */}
            <div className="lg:w-1/2 w-full flex items-center justify-center p-6 lg:p-12">
                <div className="w-full max-w-[520px] animate-fade-up delay-1000">
                    <div className="bg-white rounded-[24px] p-10 lg:p-14 shadow-2xl border border-[#E6E8EE] relative">

                        <div className="absolute -top-7 left-1/2 -translate-x-1/2 w-14 h-14 bg-white rounded-2xl shadow-xl border border-[#E6E8EE] flex items-center justify-center">
                            <ShieldCheck className="w-7 h-7 text-[#0F766E]" />
                        </div>

                        <div className="flex justify-end mb-4">
                            <select
                                value={lang}
                                onChange={(e) => setLang(e.target.value)}
                                className="border border-[#E6E8EE] rounded-xl bg-white px-3 py-2 text-sm font-semibold text-[#172033] outline-none focus:border-[#0F766E]"
                            >
                                <option value="en">🌐 English</option>
                                <option value="hi">🌐 हिन्दी</option>
                                <option value="te">🌐 తెలుగు</option>
                                <option value="mr">🌐 मराठी</option>
                            </select>
                        </div>

                        <div className="text-center mt-4 mb-10">
                            <h2 className="text-3xl font-bold text-[#172033]">{t.welcomeText} <span className="text-[#0F766E]">{t.welcomeBack}</span></h2>
                            <p className="text-[#667085] mt-2 font-medium">{t.welcomeDescription}</p>
                        </div>

                        {/* Segmented Control */}
                        <div className="flex p-1.5 bg-[#F8F7F4] rounded-2xl mb-10 border border-[#E6E8EE]">
                            <button
                                onClick={() => setLoginMethod('email')}
                                className={`flex-1 py-3 text-sm font-bold rounded-xl transition-all ${loginMethod === 'email' ? 'bg-[#1E2A5A] text-white shadow-lg' : 'text-[#667085]'}`}
                            >
                                {t.passwordLogin}
                            </button>
                            <button
                                onClick={() => setLoginMethod('mobile')}
                                className={`flex-1 py-3 text-sm font-bold rounded-xl transition-all ${loginMethod === 'mobile' ? 'bg-[#1E2A5A] text-white shadow-lg' : 'text-[#667085]'}`}
                            >
                                {t.mobileOTP}
                            </button>
                        </div>

                        <form onSubmit={handleLogin} className="space-y-6">
                            {/* Email/Mobile Field */}
                            <div className="space-y-2">
                                <label className="text-sm font-bold text-[#172033] ml-1">
                                    {loginMethod === 'email' ? t.emailLabel : t.mobileLabel}
                                </label>
                                <div className="relative group">
                                    <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-[#667085] group-focus-within:text-[#0F766E]">
                                        {loginMethod === 'email' ? <Mail size={20} /> : <Smartphone size={20} />}
                                    </span>
                                    <input
                                        type={loginMethod === 'email' ? "email" : "tel"}
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder={loginMethod === 'email' ? t.emailPlaceholder : t.mobilePlaceholder}
                                        className="w-full pl-12 pr-4 py-4 bg-white border border-[#E6E8EE] rounded-2xl outline-none transition-all input-focus text-[#172033] font-medium"
                                    />
                                </div>
                            </div>

                            {/* Password Field (For both Email and Mobile OTP mode) */}
                            {(loginMethod === 'email' || loginMethod === 'mobile') && (
                                <div className="space-y-2">
                                    <label className="text-sm font-bold text-[#172033] ml-1">{t.passwordLabel}</label>
                                    <div className="relative group">
                                        <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-[#667085] group-focus-within:text-[#0F766E]">
                                            <Lock size={20} />
                                        </span>
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder={t.passwordPlaceholder}
                                            className="w-full pl-12 pr-12 py-4 bg-white border border-[#E6E8EE] rounded-2xl outline-none transition-all input-focus text-[#172033] font-medium"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute inset-y-0 right-0 pr-4 flex items-center text-[#667085] hover:text-[#0F766E]"
                                        >
                                            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                        </button>
                                    </div>
                                </div>
                            )}

                            <div className="flex items-center justify-between px-1">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input type="checkbox" className="w-4 h-4 rounded border-[#E6E8EE] text-[#0F766E] focus:ring-[#0F766E]" />
                                    <span className="text-sm font-semibold text-[#667085] group-hover:text-[#172033]">{t.rememberMe}</span>
                                </label>
                                {loginMethod === 'email' && <a href="#" className="text-sm font-bold text-[#1E2A5A] hover:text-[#0F766E] transition-colors">{t.forgotPassword}</a>}
                            </div>

                                                        {error && (
                                <p className="text-red-500 text-sm text-center">
                                    {error}
                                </p>
                            )}

                            <button
                                type="submit"
                                className="w-full py-4 bg-[#1E2A5A] hover:bg-[#2a3a7a] text-white font-bold rounded-2xl transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 shadow-xl shadow-[#1E2A5A]/10 mt-4"
                            >
                                {loading ? "Signing in..." : t.signIn}
                                <ArrowRight size={20} />
                            </button>
                        </form>

                        <div className="mt-10 text-center">
                            <p className="text-[#667085] font-semibold text-sm">
                                {t.newToAarogya}
                                <a href="#" className="text-[#0F766E] font-extrabold hover:underline ml-1">{t.createAccount}</a>
                            </p>
                        </div>

                        <div className="mt-10 pt-8 border-t border-[#F8F7F4] flex items-center justify-center gap-3 text-[#667085]">
                            <div className="p-2 bg-[#CFF7F2] rounded-lg">
                                <ShieldCheck size={16} className="text-[#0F766E]" />
                            </div>
                            <span className="text-xs font-bold tracking-tight">{t.securityMessage}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PatientLogin;