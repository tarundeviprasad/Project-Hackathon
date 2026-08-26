import React, { useState, useEffect } from 'react';
import { 
  Bell, HelpCircle, User, Menu, X, PhoneCall, 
  Stethoscope, Calendar, ClipboardList, Route, 
  TestTube, Pill, MapPin, MessageCircleHeart, 
  ChevronRight, ArrowRight, HeartPulse, Activity,
  LogOut, LayoutDashboard, Search, Clock, ChevronDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AarogyaDashboard = () => {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  // Brand Palette Mapping
  const colors = {
    primary: "#1E2A5A",    // Deep Indigo
    accent: "#0F766E",     // Rich Teal
    highlight: "#CFF7F2",  // Soft Aqua
    bg: "#F8F7F4",         // Soft Ivory
    card: "#FFFFFF",       // Pure White
    textMain: "#172033",   // Charcoal Navy
    textSec: "#667085",    // Slate Gray
    border: "#E6E8EE",     // Soft Gray
    emergency: "#B91C1C"   // Deep Professional Red
  };

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth < 1024) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const featureCards = [
    { title: "Consult Doctor", sub: "Talk to a doctor online or find the right specialist.", icon: Stethoscope, status: "Doctors Available", statusColor: "text-[#0F766E] bg-[#CFF7F2]" },
    { title: "Appointments & Queue", sub: "Book appointments and check your current queue.", icon: Clock, status: "Queue: #04", statusColor: "text-[#1E2A5A] bg-[#E0E7FF]" },
    { title: "Health Records", sub: "View your medical history, prescriptions and reports.", icon: ClipboardList, status: "Last: 12 Aug", statusColor: "text-slate-600 bg-slate-100" },
    { title: "Referral Tracking", sub: "Track your referral from one healthcare centre to another.", icon: Route, status: "Visit Pending", statusColor: "text-amber-700 bg-amber-50" },
    { title: "Diagnostics & Reports", sub: "View diagnostic tests, results and medical reports.", icon: TestTube, status: "Report Ready", statusColor: "text-[#0F766E] bg-[#CFF7F2]" },
    { title: "Medicines Availability", sub: "Check whether medicines are available nearby.", icon: Pill, status: "In Stock", statusColor: "text-[#0F766E] bg-[#CFF7F2]" },
    { title: "Healthcare Centres", sub: "Find nearby hospitals, PHCs and health centres.", icon: MapPin, status: "2.4 km away", statusColor: "text-slate-600 bg-slate-100" },
    { title: "Digital Triage", sub: "Describe symptoms and understand the next steps.", icon: MessageCircleHeart, status: "Start Now", statusColor: "text-[#1E2A5A] bg-[#CFF7F2]" },
  ];

  return (
    <div style={{ backgroundColor: colors.bg, color: colors.textMain }} className="min-h-screen flex font-sans antialiased">
      
      {/* SIDEBAR */}
      {!isMobile && (
        <aside 
          style={{ width: isSidebarOpen ? '280px' : '80px', borderColor: colors.border, backgroundColor: colors.card }}
          className="border-r transition-all duration-300 flex flex-col sticky top-0 h-screen z-40"
        >
          <div className="p-6 flex items-center gap-3">
            <div style={{ backgroundColor: colors.primary }} className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 shadow-lg">
              <HeartPulse className="text-white w-6 h-6" />
            </div>
            {isSidebarOpen && <span style={{ color: colors.primary }} className="font-black text-xl tracking-tight">AarogyaConnect</span>}
          </div>

          <nav className="flex-1 px-4 space-y-1 mt-4">
            {[
              { name: 'Dashboard', icon: LayoutDashboard, active: true },
              { name: 'Consult Doctor', icon: Stethoscope },
              { name: 'Appointments', icon: Calendar },
              { name: 'Health Records', icon: ClipboardList },
              { name: 'Medicines', icon: Pill },
              { name: 'Help & Support', icon: HelpCircle },
            ].map((item) => (
              <button 
                key={item.name} 
                style={{ backgroundColor: item.active ? colors.highlight : 'transparent' }}
                className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all group`}
              >
                <item.icon size={22} style={{ color: item.active ? colors.accent : colors.textSec }} />
                {isSidebarOpen && <span className={`font-semibold ${item.active ? 'text-[#0F766E]' : 'text-slate-500 group-hover:text-[#172033]'}`}>{item.name}</span>}
              </button>
            ))}
          </nav>

          <div className="p-4 border-t" style={{ borderColor: colors.border }}>
            <button className="w-full flex items-center gap-4 px-4 py-3 text-rose-600 hover:bg-rose-50 rounded-xl transition-all font-bold">
              <LogOut size={22} />
              {isSidebarOpen && <span>Logout</span>}
            </button>
          </div>
        </aside>
      )}

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        
        {/* HEADER */}
        <header style={{ backgroundColor: 'rgba(255,255,255,0.8)', borderColor: colors.border }} className="backdrop-blur-md border-b sticky top-0 z-30 px-6 lg:px-10 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {isMobile && <Menu style={{ color: colors.textMain }} onClick={() => setSidebarOpen(true)} />}
            <div>
              <h1 style={{ color: colors.textMain }} className="text-xl lg:text-2xl font-black">Good morning, Vinay 👋</h1>
              <p style={{ color: colors.textSec }} className="text-sm font-medium">How can we help you today?</p>
            </div>
          </div>

          <div className="flex items-center gap-3 lg:gap-6">
             <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full border" style={{ borderColor: colors.border, backgroundColor: colors.bg }}>
                <Search size={18} style={{ color: colors.textSec }} />
                <input type="text" placeholder="Search services..." className="bg-transparent border-none focus:outline-none text-sm w-40" />
             </div>
            <button style={{ color: colors.textSec }} className="p-2 hover:bg-white rounded-full relative">
              <Bell size={22} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
            </button>
            <div className="flex items-center gap-3 pl-4 border-l" style={{ borderColor: colors.border }}>
              <div className="text-right hidden sm:block">
                <p className="text-sm font-bold">Vinay Kumar</p>
                <p style={{ color: colors.accent }} className="text-[10px] font-black uppercase tracking-widest">O+ Positive</p>
              </div>
              <div className="w-10 h-10 bg-slate-200 rounded-full border shadow-sm flex items-center justify-center overflow-hidden">
                <User size={20} className="text-slate-500" />
              </div>
              <ChevronDown size={16} style={{ color: colors.textSec }} />
            </div>
          </div>
        </header>

        <div className="p-6 lg:p-10 max-w-7xl mx-auto w-full space-y-8">
          
          {/* PROFILE SUMMARY & EMERGENCY ROW */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            
            {/* EMERGENCY BUTTON (High Visibility) */}
            <motion.div 
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              style={{ backgroundColor: colors.emergency }}
              className="lg:col-span-4 rounded-3xl p-6 text-white shadow-2xl shadow-red-200 flex flex-col justify-between relative overflow-hidden cursor-pointer"
            >
              <div className="relative z-10">
                <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center mb-4">
                  <PhoneCall size={28} className="animate-pulse" />
                </div>
                <h2 className="text-2xl font-black">Emergency Help</h2>
                <p className="opacity-80 text-sm font-medium mt-1">Get urgent medical assistance now</p>
              </div>
              <div className="relative z-10 mt-8 flex items-center gap-2 font-bold bg-white/10 w-fit px-4 py-2 rounded-full">
                Call Ambulance <ArrowRight size={16} />
              </div>
              <HeartPulse size={120} className="absolute -right-8 -bottom-8 opacity-10" />
            </motion.div>

            {/* PROFILE CARD */}
            <div style={{ backgroundColor: colors.card, borderColor: colors.border }} className="lg:col-span-8 rounded-3xl p-6 border shadow-sm flex flex-col md:flex-row items-center gap-8">
               <div className="flex items-center gap-6 flex-1">
                  <div style={{ backgroundColor: colors.highlight }} className="w-20 h-20 rounded-2xl flex items-center justify-center">
                    <User size={40} style={{ color: colors.accent }} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black">Vinay Kumar</h3>
                    <p style={{ color: colors.textSec }} className="font-medium">20 years • Male • <span className="text-rose-600 font-bold">Blood Group: O+</span></p>
                    <button style={{ color: colors.primary }} className="text-sm font-bold mt-2 flex items-center gap-1 hover:underline">
                      View Full Medical Profile <ChevronRight size={14} />
                    </button>
                  </div>
               </div>
               <div className="w-full md:w-px h-px md:h-12 bg-slate-100"></div>
               <div className="flex gap-8">
                  <div className="text-center">
                    <p style={{ color: colors.textSec }} className="text-xs font-bold uppercase tracking-widest mb-1">Height</p>
                    <p className="text-xl font-black">175 cm</p>
                  </div>
                  <div className="text-center">
                    <p style={{ color: colors.textSec }} className="text-xs font-bold uppercase tracking-widest mb-1">Weight</p>
                    <p className="text-xl font-black">68 kg</p>
                  </div>
               </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* MAIN FEATURE GRID */}
            <div className="lg:col-span-2">
              <div className="mb-6">
                <h3 className="text-xl font-black">Your Healthcare Services</h3>
                <p style={{ color: colors.textSec }} className="font-medium">Everything you need, in one place.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {featureCards.map((card, idx) => (
                  <motion.div 
                    key={idx}
                    whileHover={{ y: -4, borderColor: colors.accent }}
                    style={{ backgroundColor: colors.card, borderColor: colors.border }}
                    className="p-6 rounded-3xl border shadow-sm cursor-pointer group transition-all"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div style={{ backgroundColor: colors.highlight }} className="p-3 rounded-2xl transition-colors group-hover:bg-[#0F766E] group-hover:text-white">
                        <card.icon size={26} style={{ color: 'inherit' }} className="text-[#0F766E] group-hover:text-white" />
                      </div>
                      <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${card.statusColor}`}>
                        {card.status}
                      </span>
                    </div>
                    <h4 className="text-lg font-black mb-1">{card.title}</h4>
                    <p style={{ color: colors.textSec }} className="text-sm leading-relaxed mb-4">{card.sub}</p>
                    <div style={{ color: colors.primary }} className="flex items-center text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                      Open Service <ChevronRight size={14} className="ml-1" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* SIDEBAR INFO PANELS */}
            <div className="space-y-6">
              
              {/* UPCOMING APPOINTMENT */}
              <div style={{ backgroundColor: colors.primary }} className="rounded-3xl p-6 text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-6">
                    <span className="bg-white/20 px-3 py-1 rounded-full text-[10px] font-bold uppercase">Next Appointment</span>
                    <Clock size={20} className="opacity-60" />
                  </div>
                  <h4 className="text-xl font-black">Dr. Ananya Sharma</h4>
                  <p className="opacity-70 text-sm">General Physician</p>
                  
                  <div className="mt-6 flex items-center gap-4 bg-white/10 p-4 rounded-2xl">
                    <Calendar size={20} className="text-[#CFF7F2]" />
                    <div>
                      <p className="text-[10px] opacity-60 font-bold uppercase">Today • 10:30 AM</p>
                      <p className="text-sm font-bold">District Health Centre</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mt-6">
                    <button className="py-3 bg-white text-[#1E2A5A] rounded-xl font-bold text-xs hover:bg-slate-100 transition-all">Join Live</button>
                    <button className="py-3 bg-white/10 border border-white/20 rounded-xl font-bold text-xs hover:bg-white/20 transition-all">Details</button>
                  </div>
                </div>
              </div>

              {/* HEALTH SNAPSHOT */}
              <div style={{ backgroundColor: colors.card, borderColor: colors.border }} className="rounded-3xl p-6 border shadow-sm">
                <h4 className="font-black mb-4">Health Snapshot</h4>
                <div className="space-y-3">
                  {[
                    { label: 'Blood Pressure', val: '120/80', stat: 'Normal', icon: Activity, col: 'text-emerald-600', bg: 'bg-emerald-50' },
                    { label: 'Heart Rate', val: '72 BPM', stat: 'Steady', icon: HeartPulse, col: 'text-rose-600', bg: 'bg-rose-50' }
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-3 rounded-2xl border border-slate-50 bg-slate-50/50">
                      <div className={`w-10 h-10 ${item.bg} ${item.col} rounded-xl flex items-center justify-center`}>
                        <item.icon size={20} />
                      </div>
                      <div className="flex-1">
                        <p style={{ color: colors.textSec }} className="text-[10px] font-bold uppercase">{item.label}</p>
                        <p className="font-black text-sm">{item.val}</p>
                      </div>
                      <span className={`text-[10px] font-bold ${item.col}`}>{item.stat}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* MEDICINE REMINDER */}
              <div style={{ backgroundColor: colors.highlight, borderColor: colors.accent }} className="rounded-3xl p-6 border-l-4 shadow-sm">
                 <div className="flex items-center gap-3 mb-2">
                    <Pill style={{ color: colors.accent }} size={20} />
                    <h4 className="font-black text-sm" style={{ color: colors.accent }}>Medicine Reminder</h4>
                 </div>
                 <p style={{ color: colors.textMain }} className="text-sm font-bold">Paracetamol 500mg</p>
                 <p style={{ color: colors.textSec }} className="text-xs">Take after lunch • 02:00 PM</p>
              </div>

            </div>
          </div>
        </div>

        {/* MOBILE NAVIGATION */}
        {isMobile && (
          <div style={{ backgroundColor: colors.card, borderColor: colors.border }} className="fixed bottom-0 left-0 right-0 border-t px-8 py-4 flex justify-between items-center z-50 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
            <LayoutDashboard size={24} style={{ color: colors.primary }} />
            <Calendar size={24} style={{ color: colors.textSec }} />
            <div style={{ backgroundColor: colors.primary }} className="w-12 h-12 rounded-2xl flex items-center justify-center -mt-10 shadow-lg border-4 border-white">
              <PhoneCall size={20} className="text-white" />
            </div>
            <ClipboardList size={24} style={{ color: colors.textSec }} />
            <User size={24} style={{ color: colors.textSec }} />
          </div>
        )}
      </main>
    </div>
  );
};

export default AarogyaDashboard;