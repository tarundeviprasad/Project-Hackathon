import React, { useState } from 'react';
import {
    LayoutDashboard, ClipboardCheck, Users, CalendarClock, Video,
    Pill, HeartPulse, Send, Headset, LogOut, Bell, Search,
    ChevronRight, Stethoscope, Activity, MapPin, CheckCircle,
    AlertTriangle, Clock, ShieldAlert, Phone, UserRound,
    MoreVertical, Camera, Mic, MicOff, VideoOff, PhoneOff, ShieldCheck
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- THEME CONSTANTS ---
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

// --- MOCK DATA ---
const DOCTOR_INFO = {
    name: "Dr. Arjun Mehta",
    specialty: "General Physician",
    facility: "Primary Health Centre - Zone A",
    status: "Available"
};

const QUEUE_DATA = [
    { id: "P-1024", name: "Rajesh Kumar", time: "09:30 AM", type: "In-person", priority: "Normal", status: "Waiting" },
    { id: "P-1031", name: "Sunita Devi", time: "09:45 AM", type: "Teleconsult", priority: "Priority", status: "In Consultation" },
    { id: "P-1044", name: "Amit Sharma", time: "10:00 AM", type: "In-person", priority: "Normal", status: "Waiting" },
];

const HIGH_RISK_ALERTS = [
    { id: "P-2045", risk: "Critical", issue: "Hypertension Follow-up", due: "Today" },
    { id: "P-2112", risk: "High", issue: "Post-Surgical Check", due: "Tomorrow" },
];

// --- SUB-COMPONENTS ---

const StatusBadge = ({ status }) => {
    const styles = {
        'Waiting': 'bg-gray-100 text-[#1E2A5A]',
        'In Consultation': 'bg-[#CFF7F2] text-[#0F766E]',
        'Completed': 'bg-green-100 text-green-700',
        'Priority': 'bg-amber-100 text-amber-700',
        'Critical': 'bg-red-100 text-red-700',
    };
    return (
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${styles[status] || styles['Waiting']}`}>
            {status}
        </span>
    );
};

const SidebarItem = ({ icon: Icon, label, active, onClick, badge }) => (
    <button
        onClick={onClick}
        className={`w-full flex items-center justify-between px-6 py-4 transition-all border-l-4 ${active
            ? 'bg-[#CFF7F2] border-[#0F766E] text-[#1E2A5A]'
            : 'bg-transparent border-transparent text-[#667085] hover:bg-gray-50'
            }`}
    >
        <div className="flex items-center gap-4">
            <Icon size={20} className={active ? 'text-[#0F766E]' : 'text-[#667085]'} />
            <span className={`font-medium text-sm ${active ? 'font-bold' : ''}`}>{label}</span>
        </div>
        {badge && (
            <span className="bg-[#1E2A5A] text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                {badge}
            </span>
        )}
    </button>
);

const SummaryCard = ({ icon: Icon, label, value, subtext, color }) => (
    <div className="bg-white p-6 rounded-2xl border border-[#E6E8EE] shadow-sm flex items-start gap-4">
        <div className="p-3 rounded-xl" style={{ backgroundColor: color + '20' }}>
            <Icon size={24} style={{ color: color }} />
        </div>
        <div>
            <p className="text-2xl font-bold text-[#172033]">{value}</p>
            <p className="text-xs font-bold text-[#667085] uppercase tracking-wider mt-1">{label}</p>
            <p className="text-[10px] text-[#667085] mt-2">{subtext}</p>
        </div>
    </div>
);

// --- MAIN PORTAL COMPONENTS ---

const DashboardView = () => (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
        <header>
            <h2 className="text-2xl font-bold text-[#1E2A5A]">Good morning, {DOCTOR_INFO.name}</h2>
            <p className="text-[#667085] text-sm mt-1">Here is your healthcare activity overview for today.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <SummaryCard icon={CalendarClock} label="Today's Appointments" value="24" subtext="8 completed" color="#1E2A5A" />
            <SummaryCard icon={Users} label="Patients Waiting" value="06" subtext="Current queue" color="#0F766E" />
            <SummaryCard icon={Video} label="Teleconsultations" value="05" subtext="2 currently waiting" color="#0F766E" />
            <SummaryCard icon={ShieldAlert} label="High-Risk Patients" value="03" subtext="Require follow-up" color="#dc2626" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* QUEUE TABLE */}
            <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E6E8EE] shadow-sm overflow-hidden">
                <div className="p-6 border-b border-[#E6E8EE] flex justify-between items-center">
                    <h3 className="font-bold text-[#1E2A5A]">Today's Patient Queue</h3>
                    <button className="text-[#0F766E] text-xs font-bold hover:underline">Open Queue →</button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-[#F8F7F4] text-[10px] font-black text-[#667085] uppercase tracking-widest">
                            <tr>
                                <th className="px-6 py-4">Patient ID</th>
                                <th className="px-6 py-4">Name</th>
                                <th className="px-6 py-4">Time</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[#E6E8EE]">
                            {QUEUE_DATA.map((item) => (
                                <tr key={item.id} className="hover:bg-gray-50 transition-colors group">
                                    <td className="px-6 py-4 text-xs font-bold text-[#667085]">{item.id}</td>
                                    <td className="px-6 py-4 text-sm font-bold text-[#1E2A5A]">{item.name}</td>
                                    <td className="px-6 py-4 text-xs text-[#667085] font-medium">{item.time}</td>
                                    <td className="px-6 py-4"><StatusBadge status={item.status} /></td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-[#0F766E] font-bold text-xs hover:underline">Consult</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* ALERTS & MEDICINE */}
            <div className="space-y-8">
                <div className="bg-white p-6 rounded-2xl border border-red-100 shadow-sm">
                    <h3 className="font-bold text-[#1E2A5A] mb-4 flex items-center gap-2">
                        <ShieldAlert size={18} className="text-red-600" /> High-Risk Alerts
                    </h3>
                    <div className="space-y-4">
                        {HIGH_RISK_ALERTS.map(alert => (
                            <div key={alert.id} className="p-4 bg-red-50 rounded-xl border border-red-100 flex items-center justify-between">
                                <div>
                                    <p className="text-xs font-bold text-red-700">Patient #{alert.id}</p>
                                    <p className="text-xs text-red-600 font-medium">{alert.issue}</p>
                                </div>
                                <StatusBadge status={alert.risk} />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white p-6 rounded-2xl border border-[#E6E8EE] shadow-sm">
                    <h3 className="font-bold text-[#1E2A5A] mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-2 gap-3">
                        {[
                            { label: "Triage", icon: ClipboardCheck },
                            { label: "Patient", icon: Users },
                            { label: "Referral", icon: Send },
                            { label: "Call Next", icon: ChevronRight },
                        ].map(action => (
                            <button key={action.label} className="p-3 bg-[#F8F7F4] hover:bg-[#CFF7F2] rounded-xl flex flex-col items-center gap-2 transition-colors border border-[#E6E8EE]">
                                <action.icon size={18} className="text-[#0F766E]" />
                                <span className="text-[10px] font-bold uppercase tracking-wider text-[#1E2A5A]">{action.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    </motion.div>
);

// --- MAIN PORTAL SHELL ---

export default function DoctorPortal() {
    const [activeTab, setActiveTab] = useState('Dashboard');
    const [showNotifications, setShowNotifications] = useState(false);

    const menuItems = [
        { id: 'Dashboard', icon: LayoutDashboard },
        { id: 'Digital Triage', icon: ClipboardCheck, badge: 'New' },
        { id: 'Patient Portal', icon: Users },
        { id: 'Appointments', icon: CalendarClock },
        { id: 'Teleconsultation', icon: Video },
        { id: 'Medicine Availability', icon: Pill },
        { id: 'High-Risk Patients', icon: HeartPulse, badge: '3' },
        { id: 'Referrals', icon: Send },
    ];

    return (
        <div className="flex h-screen bg-[#F8F7F4] font-sans text-[#172033] overflow-hidden">

            {/* FIXED SIDEBAR */}
            <aside className="w-72 bg-white border-r border-[#E6E8EE] flex flex-col z-30 shadow-sm">
                <div className="p-8 flex items-center gap-3">
                    <div className="w-10 h-10 bg-[#1E2A5A] rounded-xl flex items-center justify-center text-white shadow-lg">
                        <HeartPulse size={24} />
                    </div>
                    <div>
                        <h1 className="text-xl font-black text-[#1E2A5A] tracking-tight uppercase leading-none">Aarogya</h1>
                        <p className="text-[10px] font-bold text-[#0F766E] tracking-[0.2em] uppercase leading-none mt-1">Connect</p>
                    </div>
                </div>

                <nav className="flex-1 py-4 overflow-y-auto">
                    {menuItems.map(item => (
                        <SidebarItem
                            key={item.id}
                            icon={item.icon}
                            label={item.id}
                            active={activeTab === item.id}
                            badge={item.badge}
                            onClick={() => setActiveTab(item.id)}
                        />
                    ))}

                    <div className="px-8 pt-8 pb-4">
                        <span className="text-[10px] font-black text-[#667085] tracking-[0.3em] uppercase">Support</span>
                    </div>
                    <SidebarItem icon={Headset} label="Customer Service" active={activeTab === 'Support'} onClick={() => setActiveTab('Support')} />
                    <SidebarItem icon={LogOut} label="Logout" onClick={() => window.location.href = '/'} />
                </nav>

                <div className="p-6 border-t border-[#E6E8EE]">
                    <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-100 rounded-xl">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <div>
                            <p className="text-xs font-bold text-[#1E2A5A]">{DOCTOR_INFO.status}</p>
                            <p className="text-[10px] text-green-700 font-medium">Accepting Patients</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* MAIN CONTENT AREA */}
            <div className="flex-1 flex flex-col relative overflow-hidden">

                {/* HEADER */}
                <header className="h-20 bg-white border-b border-[#E6E8EE] flex items-center justify-between px-10 z-20 shadow-sm">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2 px-4 py-2 bg-[#F8F7F4] rounded-xl border border-[#E6E8EE]">
                            <MapPin size={16} className="text-[#0F766E]" />
                            <span className="text-xs font-bold text-[#1E2A5A]">{DOCTOR_INFO.facility}</span>
                        </div>
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#667085]" size={16} />
                            <input
                                type="text"
                                placeholder="Search patient, ID, records..."
                                className="pl-10 pr-4 py-2 bg-white border border-[#E6E8EE] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#0F766E]/20 w-64 transition-all"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="relative">
                            <button
                                onClick={() => setShowNotifications(!showNotifications)}
                                className="p-2.5 bg-[#F8F7F4] rounded-xl text-[#1E2A5A] hover:bg-[#E6E8EE] transition-all relative"
                            >
                                <Bell size={20} />
                                <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full"></span>
                            </button>

                            <AnimatePresence>
                                {showNotifications && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
                                        className="absolute right-0 mt-3 w-80 bg-white border border-[#E6E8EE] shadow-2xl rounded-2xl z-50 overflow-hidden"
                                    >
                                        <div className="p-4 border-b border-[#E6E8EE] font-bold text-[#1E2A5A]">Notifications</div>
                                        <div className="p-4 border-b border-gray-50 hover:bg-gray-50">
                                            <p className="text-xs font-bold text-[#0F766E]">High-Risk Follow-up</p>
                                            <p className="text-xs text-[#172033] mt-1">Patient #P-2045 requires follow-up today.</p>
                                        </div>
                                        <div className="p-4 hover:bg-gray-50">
                                            <p className="text-xs font-bold text-[#1E2A5A]">Queue Update</p>
                                            <p className="text-xs text-[#172033] mt-1">New priority patient added to queue.</p>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        <div className="flex items-center gap-4 pl-6 border-l border-[#E6E8EE]">
                            <div className="text-right">
                                <p className="text-sm font-bold text-[#1E2A5A]">{DOCTOR_INFO.name}</p>
                                <p className="text-[10px] text-[#0F766E] font-bold uppercase tracking-wider">{DOCTOR_INFO.specialty}</p>
                            </div>
                            <div className="w-10 h-10 rounded-xl bg-[#1E2A5A] flex items-center justify-center text-white font-bold text-sm">
                                AM
                            </div>
                        </div>
                    </div>
                </header>

                {/* WORKSPACE */}
                <main className="flex-1 overflow-y-auto p-10">
                    <div className="max-w-7xl mx-auto">
                        {activeTab === 'Dashboard' ? <DashboardView /> : (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-white rounded-[2rem] border border-[#E6E8EE] p-20 flex flex-col items-center justify-center text-center space-y-4"
                            >
                                <div className="w-20 h-20 bg-[#F8F7F4] rounded-full flex items-center justify-center text-[#CFF7F2]">
                                    <Activity size={40} />
                                </div>
                                <h3 className="text-2xl font-bold text-[#1E2A5A]">{activeTab} Module</h3>
                                <p className="text-[#667085] max-w-sm">This module is currently being optimized for clinical workflows in rural healthcare centres.</p>
                                <button
                                    onClick={() => setActiveTab('Dashboard')}
                                    className="mt-4 px-6 py-2 bg-[#0F766E] text-white rounded-xl font-bold text-sm"
                                >
                                    Return to Dashboard
                                </button>
                            </motion.div>
                        )}
                    </div>
                </main>

                {/* AI DECISION SUPPORT FOOTER (Subtle) */}
                <footer className="h-12 bg-[#1E2A5A] flex items-center justify-center px-10">
                    <div className="flex items-center gap-2 text-white/60 text-[10px] font-bold uppercase tracking-widest">
                        <ShieldCheck size={14} />
                        <span>AI Clinical Decision Support Active • Verified Clinical Guidance</span>
                    </div>
                </footer>
            </div>
        </div>
    );
}