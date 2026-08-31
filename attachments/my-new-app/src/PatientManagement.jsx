import React, { useState, useMemo } from 'react';
import {
    Search, User, Phone, IdCard, Calendar,
    ChevronRight, ArrowLeft, History, FileText,
    Beaker, AlertTriangle, Plus, Clipboard,
    Stethoscope, LayoutDashboard, Users,
    ArrowRightLeft, Headset, HelpCircle,
    HeartPulse, Globe, X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- THEME CONSTANTS (Exact Palette) ---
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

// --- TRANSLATIONS ---
const TRANSLATIONS = {
    en: {
        title: "Patient Management",
        subtitle: "Search and access complete patient health information.",
        placeholder: "Search by Patient ID, ABHA ID, Patient Name, or Phone Number",
        searchBtn: "Search",
        allPatients: "All Patients",
        helperText: "Select a patient from the list or search for a specific patient above.",
        colName: "Patient Name",
        colId: "Patient ID",
        colAbha: "ABHA ID",
        colStatus: "Status",
        btnProfile: "View Profile",
        btnBack: "Back to List",
        btnConsult: "Start Consultation",
        tabs: ["Medical History", "Consultations", "Prescriptions", "Lab Reports", "Allergies"],
        empty: "No patients found matching your search."
    },
    hi: {
        title: "रोगी प्रबंधन",
        subtitle: "रोगी की स्वास्थ्य जानकारी खोजें और एक्सेस करें।",
        placeholder: "रोगी आईडी, आभा आईडी, नाम या फोन नंबर से खोजें",
        searchBtn: "खोजें",
        allPatients: "सभी रोगी",
        helperText: "सूची से रोगी चुनें या ऊपर खोजें।",
        colName: "रोगी का नाम",
        colId: "रोगी आईडी",
        colAbha: "आभा आईडी",
        colStatus: "स्थिति",
        btnProfile: "प्रोफ़ाइल देखें",
        btnBack: "सूची पर वापस जाएं",
        btnConsult: "परामर्श शुरू करें",
        tabs: ["चिकित्सा इतिहास", "परामर्श", "नुस्खे", "लैब रिपोर्ट", "एलर्जी"],
        empty: "आपकी खोज से मेल खाता कोई रोगी नहीं मिला।"
    },
    te: {
        title: "రోగి నిర్వహణ",
        subtitle: "రోగి పూర్తి ఆరోగ్య సమాచారాన్ని శోధించండి మరియు యాక్సెస్ చేయండి.",
        placeholder: "పేషెంట్ ఐడి, అభా ఐడి, పేరు లేదా ఫోన్ నంబర్ ద్వారా శోధించండి",
        searchBtn: "శోధించండి",
        allPatients: "అందరూ రోగులు",
        helperText: "జాబితా నుండి రోగిని ఎంచుకోండి లేదా పైన శోధించండి.",
        colName: "రోగి పేరు",
        colId: "పేషెంట్ ఐడి",
        colAbha: "అభా ఐడి",
        colStatus: "స్థితి",
        btnProfile: "ప్రొఫైల్ చూడండి",
        btnBack: "జాబితాకు తిరిగి వెళ్ళు",
        btnConsult: "సంప్రదింపులు ప్రారంభించండి",
        tabs: ["వైద్య చరిత్ర", "సంప్రదింపులు", "మందుల చీటి", "ల్యాబ్ రిపోర్టులు", "అలర్జీలు"],
        empty: "మీ శోధనకు సరిపోలే రోగులు ఎవరూ లేరు."
    },
    mr: {
        title: "रुग्ण व्यवस्थापन",
        subtitle: "रुग्णाची संपूर्ण आरोग्य माहिती शोधा आणि प्रवेश करा.",
        placeholder: "रुग्ण आयडी, आभा आयडी, नाव किंवा फोन नंबरद्वारे शोधा",
        searchBtn: "शोधा",
        allPatients: "सर्व रुग्ण",
        helperText: "सूचीमधून रुग्ण निवडा किंवा वर शोधा.",
        colName: "रुग्णाचे नाव",
        colId: "रुग्ण आयडी",
        colAbha: "आभा आयडी",
        colStatus: "स्थिती",
        btnProfile: "प्रोफाइल पहा",
        btnBack: "सूचीकडे परत",
        btnConsult: "परामर्श सुरू करा",
        tabs: ["वैद्यकीय इतिहास", "परामर्श", "औषधोपचार", "लॅब रिपोर्ट्स", "एलर्जी"],
        empty: "तुमच्या शोधाशी जुळणारा कोणताही रुग्ण आढळला नाही."
    }
};

// --- DUMMY DATA ---
const PATIENTS = [
    { id: "P-1001", abhaId: "91-2234-5567-0012", name: "Ravi Kumar", age: 45, gender: "Male", phone: "9876543210", lastConsult: "2024-05-12", status: "Active", blood: "O+", allergies: ["Penicillin"], chronic: ["Hypertension"] },
    { id: "P-1002", abhaId: "91-4456-1123-8890", name: "Lakshmi Devi", age: 38, gender: "Female", phone: "9822334455", lastConsult: "2024-05-10", status: "Follow-up", blood: "A-", allergies: ["Dust"], chronic: ["Diabetes Type 2"] },
    { id: "P-1003", abhaId: "91-7789-3345-1122", name: "Suresh Reddy", age: 52, gender: "Male", phone: "9100998877", lastConsult: "2024-04-25", status: "High Risk", blood: "B+", allergies: ["Sulfa"], chronic: ["Asthma"] },
    { id: "P-1004", abhaId: "91-1122-3344-5566", name: "Anjali Sharma", age: 29, gender: "Female", phone: "8877665544", lastConsult: "2024-05-15", status: "New Patient", blood: "AB+", allergies: ["Latex"], chronic: ["None"] },
    { id: "P-1005", abhaId: "91-9988-7766-5544", name: "Ramesh Naidu", age: 60, gender: "Male", phone: "7766554433", lastConsult: "2024-03-20", status: "Active", blood: "O-", allergies: ["Peanuts"], chronic: ["Cardiovascular Disease"] },
    { id: "P-1006", abhaId: "91-4433-2211-0099", name: "Priya Rani", age: 34, gender: "Female", phone: "9988443322", lastConsult: "2024-05-01", status: "Follow-up", blood: "B-", allergies: ["None"], chronic: ["Hypothyroidism"] },
    { id: "P-1007", abhaId: "91-2211-5544-8877", name: "Kiran Kumar", age: 41, gender: "Male", phone: "8899776655", lastConsult: "2024-04-18", status: "Active", blood: "A+", allergies: ["Aspirin"], chronic: ["None"] },
    { id: "P-1008", abhaId: "91-6655-4433-2211", name: "Sunitha Devi", age: 47, gender: "Female", phone: "7766112233", lastConsult: "2024-05-05", status: "High Risk", blood: "O+", allergies: ["Shellfish"], chronic: ["Chronic Kidney Disease"] },
    { id: "P-1009", abhaId: "91-0011-2233-4455", name: "Arjun Rao", age: 25, gender: "Male", phone: "9123456789", lastConsult: "2024-05-18", status: "New Patient", blood: "AB-", allergies: ["Pollen"], chronic: ["None"] },
    { id: "P-1010", abhaId: "91-5566-7788-9900", name: "Meena Kumari", age: 65, gender: "Female", phone: "9543210987", lastConsult: "2024-02-14", status: "Active", blood: "B+", allergies: ["Dairy"], chronic: ["Osteoarthritis"] },
];

// --- SUB-COMPONENTS ---

const SidebarItem = ({ icon: Icon, label, active }) => (
    <div className={`flex items-center gap-4 px-6 py-4 cursor-pointer transition-all border-l-4 ${active ? 'bg-[#CFF7F2] border-[#0F766E] text-[#1E2A5A]' : 'border-transparent text-[#667085] hover:bg-gray-50'
        }`}>
        <Icon size={20} className={active ? 'text-[#0F766E]' : 'text-[#667085]'} />
        <span className={`font-medium ${active ? 'font-bold' : ''}`}>{label}</span>
    </div>
);

const StatusBadge = ({ status }) => {
    const getStyle = () => {
        switch (status) {
            case 'Active': return 'bg-green-100 text-green-700';
            case 'High Risk': return 'bg-red-100 text-red-700';
            case 'Follow-up': return 'bg-amber-100 text-amber-700';
            case 'New Patient': return 'bg-blue-100 text-blue-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };
    return <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStyle()}`}>{status}</span>;
};

export default function PatientManagement() {
    const [lang, setLang] = useState('en');
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedPatient, setSelectedPatient] = useState(null);
    const [activeTab, setActiveTab] = useState(0);

    const t = TRANSLATIONS[lang];

    // Filter Logic
    const filteredPatients = useMemo(() => {
        return PATIENTS.filter(p =>
            p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.abhaId.includes(searchQuery) ||
            p.phone.includes(searchQuery)
        );
    }, [searchQuery]);

    return (
        <div className="flex h-screen bg-[#F8F7F4] font-sans text-[#172033] overflow-hidden">

            {/* SIDEBAR (Reference Consistent) */}
            <aside className="w-72 bg-white border-r border-[#E6E8EE] flex flex-col shadow-sm">
                <div className="p-8 flex items-center gap-3">
                    <div className="w-10 h-10 bg-[#1E2A5A] rounded-xl flex items-center justify-center text-white shadow-lg">
                        <HeartPulse size={24} />
                    </div>
                    <h1 className="text-xl font-bold text-[#1E2A5A] tracking-tight uppercase">Aarogya<span className="text-[#0F766E]">Connect</span></h1>
                </div>
                <nav className="flex-1 overflow-y-auto">
                    <SidebarItem icon={LayoutDashboard} label="Dashboard" />
                    <SidebarItem icon={Clipboard} label="Appointments" />
                    <SidebarItem icon={Users} label={t.title} active={true} />
                    <SidebarItem icon={ArrowRightLeft} label="Referrals" />
                    <div className="mt-8 px-8 py-2 text-[10px] font-bold text-[#667085] uppercase tracking-widest">Support</div>
                    <SidebarItem icon={Headset} label="Help Center" />
                    <SidebarItem icon={HelpCircle} label="FAQs" />
                </nav>
                <div className="p-6 border-t border-[#E6E8EE]">
                    <div className="flex items-center gap-3 px-4 py-2 bg-[#F8F7F4] rounded-xl cursor-pointer hover:bg-[#E6E8EE]" onClick={() => {
                        const langs = Object.keys(TRANSLATIONS);
                        const idx = langs.indexOf(lang);
                        setLang(langs[(idx + 1) % langs.length]);
                    }}>
                        <Globe size={18} className="text-[#0F766E]" />
                        <span className="text-sm font-bold text-[#1E2A5A] uppercase">{lang}</span>
                    </div>
                </div>
            </aside>

            {/* MAIN CONTENT AREA */}
            <main className="flex-1 overflow-y-auto relative">
                <AnimatePresence mode="wait">
                    {!selectedPatient ? (
                        <motion.div
                            key="list"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            className="p-10 max-w-7xl mx-auto"
                        >
                            {/* Header */}
                            <div className="mb-8">
                                <h2 className="text-3xl font-black text-[#1E2A5A]">{t.title}</h2>
                                <p className="text-[#667085] mt-1">{t.subtitle}</p>
                            </div>

                            {/* Search Section */}
                            <div className="bg-white p-6 rounded-2xl border border-[#E6E8EE] shadow-sm mb-10">
                                <div className="flex gap-4">
                                    <div className="relative flex-1 group">
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[#667085] group-focus-within:text-[#0F766E]" size={20} />
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                            placeholder={t.placeholder}
                                            className="w-full pl-12 pr-4 py-4 bg-[#F8F7F4] border border-[#E6E8EE] rounded-xl outline-none focus:border-[#0F766E] transition-all text-sm font-medium"
                                        />
                                        {searchQuery && (
                                            <button onClick={() => setSearchQuery("")} className="absolute right-4 top-1/2 -translate-y-1/2 text-[#667085] hover:text-red-500">
                                                <X size={18} />
                                            </button>
                                        )}
                                    </div>
                                    <button className="px-8 py-4 bg-[#0F766E] text-white rounded-xl font-bold hover:bg-[#0d665f] transition-all flex items-center gap-2 shadow-lg shadow-teal-900/10">
                                        <Search size={18} /> {t.searchBtn}
                                    </button>
                                </div>
                            </div>

                            {/* Patient List */}
                            <div className="bg-white rounded-2xl border border-[#E6E8EE] shadow-sm overflow-hidden">
                                <div className="p-6 border-b border-[#E6E8EE]">
                                    <h3 className="text-xl font-bold text-[#1E2A5A]">{t.allPatients}</h3>
                                    <p className="text-xs text-[#667085] mt-1">{t.helperText}</p>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left">
                                        <thead className="bg-[#F8F7F4] text-[10px] font-black text-[#667085] uppercase tracking-widest">
                                            <tr>
                                                <th className="px-6 py-4">{t.colName}</th>
                                                <th className="px-6 py-4">{t.colId}</th>
                                                <th className="px-6 py-4">{t.colAbha}</th>
                                                <th className="px-6 py-4">Age / Sex</th>
                                                <th className="px-6 py-4">{t.colStatus}</th>
                                                <th className="px-6 py-4 text-right">Action</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-[#E6E8EE]">
                                            {filteredPatients.map((patient) => (
                                                <tr key={patient.id} className="hover:bg-gray-50 transition-colors group">
                                                    <td className="px-6 py-4">
                                                        <div className="flex items-center gap-3">
                                                            <div className="w-10 h-10 bg-[#CFF7F2] rounded-full flex items-center justify-center text-[#0F766E] font-bold">
                                                                {patient.name.charAt(0)}
                                                            </div>
                                                            <span className="font-bold text-[#1E2A5A]">{patient.name}</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 text-sm font-medium text-[#667085]">{patient.id}</td>
                                                    <td className="px-6 py-4 text-sm font-medium text-[#667085]">{patient.abhaId}</td>
                                                    <td className="px-6 py-4 text-sm font-medium text-[#1E2A5A]">{patient.age} / {patient.gender.charAt(0)}</td>
                                                    <td className="px-6 py-4"><StatusBadge status={patient.status} /></td>
                                                    <td className="px-6 py-4 text-right">
                                                        <button
                                                            onClick={() => setSelectedPatient(patient)}
                                                            className="text-[#0F766E] hover:underline font-bold text-sm flex items-center gap-1 justify-end ml-auto"
                                                        >
                                                            {t.btnProfile} <ChevronRight size={16} />
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                    {filteredPatients.length === 0 && (
                                        <div className="p-20 text-center text-[#667085] font-medium">{t.empty}</div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="detail"
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.98 }}
                            className="p-10 max-w-6xl mx-auto"
                        >
                            {/* Profile Header */}
                            <button
                                onClick={() => setSelectedPatient(null)}
                                className="mb-8 flex items-center gap-2 text-[#667085] hover:text-[#1E2A5A] font-bold transition-colors"
                            >
                                <ArrowLeft size={20} /> {t.btnBack}
                            </button>

                            <div className="bg-white rounded-3xl border border-[#E6E8EE] shadow-xl overflow-hidden mb-8">
                                <div className="bg-[#1E2A5A] p-10 flex flex-col md:flex-row justify-between items-center gap-8">
                                    <div className="flex items-center gap-6">
                                        <div className="w-24 h-24 bg-[#CFF7F2] border-4 border-white/20 rounded-3xl flex items-center justify-center text-[#0F766E]">
                                            <User size={48} />
                                        </div>
                                        <div className="text-white">
                                            <h3 className="text-3xl font-black">{selectedPatient.name}</h3>
                                            <div className="flex flex-wrap gap-4 mt-2 text-white/70 text-sm font-medium">
                                                <span className="flex items-center gap-1"><IdCard size={14} /> {selectedPatient.id}</span>
                                                <span className="flex items-center gap-1"><Smartphone size={14} /> {selectedPatient.phone}</span>
                                                <span className="bg-white/10 px-2 py-0.5 rounded text-white text-xs">{selectedPatient.blood}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <button className="px-8 py-4 bg-[#0F766E] text-white rounded-2xl font-bold hover:bg-[#0d665f] transition-all flex items-center gap-2 shadow-2xl">
                                        <Stethoscope size={20} /> {t.btnConsult}
                                    </button>
                                </div>

                                {/* Tabs */}
                                <div className="flex border-b border-[#E6E8EE] px-10 overflow-x-auto bg-gray-50/50">
                                    {t.tabs.map((tab, idx) => (
                                        <button
                                            key={tab}
                                            onClick={() => setActiveTab(idx)}
                                            className={`px-6 py-5 text-sm font-bold transition-all border-b-4 whitespace-nowrap ${activeTab === idx ? 'border-[#0F766E] text-[#0F766E]' : 'border-transparent text-[#667085] hover:text-[#1E2A5A]'
                                                }`}
                                        >
                                            {tab}
                                        </button>
                                    ))}
                                </div>

                                <div className="p-10">
                                    <AnimatePresence mode="wait">
                                        {activeTab === 0 && (
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                                    <div className="space-y-4">
                                                        <h4 className="flex items-center gap-2 text-red-600 font-bold uppercase tracking-widest text-xs">
                                                            <AlertTriangle size={16} /> Allergies
                                                        </h4>
                                                        <div className="flex flex-wrap gap-2">
                                                            {selectedPatient.allergies.map(a => <span key={a} className="bg-red-50 text-red-700 px-3 py-1 rounded-lg text-sm font-bold border border-red-100">{a}</span>)}
                                                        </div>
                                                    </div>
                                                    <div className="space-y-4">
                                                        <h4 className="flex items-center gap-2 text-[#1E2A5A] font-bold uppercase tracking-widest text-xs">
                                                            <Activity size={16} /> Chronic Conditions
                                                        </h4>
                                                        <div className="flex flex-wrap gap-2">
                                                            {selectedPatient.chronic.map(c => <span key={c} className="bg-indigo-50 text-[#1E2A5A] px-3 py-1 rounded-lg text-sm font-bold border border-indigo-100">{c}</span>)}
                                                        </div>
                                                    </div>
                                                </div>
                                                <hr className="border-[#E6E8EE]" />
                                                <div className="space-y-4">
                                                    <h4 className="text-[#1E2A5A] font-bold uppercase tracking-widest text-xs">Medical Summary</h4>
                                                    <p className="text-[#667085] leading-relaxed text-sm">
                                                        Patient presents with a history of {selectedPatient.chronic[0]}. Last assessment showed stable vital signs. Continued medication as per previous prescription. No recent hospitalizations or surgical interventions noted.
                                                    </p>
                                                </div>
                                            </motion.div>
                                        )}

                                        {activeTab === 1 && (
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                                                {[1, 2].map((i) => (
                                                    <div key={i} className="p-6 bg-[#F8F7F4] rounded-2xl border border-[#E6E8EE] flex justify-between items-center group cursor-pointer hover:border-[#0F766E]">
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-[#1E2A5A] shadow-sm">
                                                                <History size={20} />
                                                            </div>
                                                            <div>
                                                                <p className="font-bold text-[#1E2A5A]">Routine Checkup</p>
                                                                <p className="text-xs text-[#667085]">Dr. Arjun Mehta • 12 May 2024</p>
                                                            </div>
                                                        </div>
                                                        <button className="p-2 bg-white rounded-lg text-[#667085] group-hover:text-[#0F766E] shadow-sm"><ChevronRight size={20} /></button>
                                                    </div>
                                                ))}
                                            </motion.div>
                                        )}

                                        {activeTab === 2 && (
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                                                <div className="p-6 border-2 border-dashed border-[#E6E8EE] rounded-2xl flex flex-col items-center justify-center text-[#667085] gap-3">
                                                    <Plus size={32} />
                                                    <span className="font-bold text-sm">Issue New Prescription</span>
                                                </div>
                                                <div className="p-6 bg-white border border-[#E6E8EE] rounded-2xl shadow-sm">
                                                    <div className="flex justify-between items-start mb-4">
                                                        <p className="font-bold text-[#1E2A5A]">Medication Plan - Post Viral</p>
                                                        <span className="text-[10px] bg-green-100 text-green-700 px-2 py-1 rounded font-bold uppercase">Active</span>
                                                    </div>
                                                    <div className="space-y-3">
                                                        <div className="flex justify-between text-sm py-2 border-b border-gray-50">
                                                            <span className="text-[#667085]">Amlodipine 5mg</span>
                                                            <span className="font-bold">1-0-1 (14 Days)</span>
                                                        </div>
                                                        <div className="flex justify-between text-sm">
                                                            <span className="text-[#667085]">Metformin 500mg</span>
                                                            <span className="font-bold">0-0-1 (30 Days)</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}

                                        {activeTab === 3 && (
                                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {[
                                                    { name: 'Full Blood Count', date: 'May 05, 2024' },
                                                    { name: 'Lipid Profile', date: 'May 05, 2024' },
                                                    { name: 'Chest X-Ray', date: 'April 12, 2024' }
                                                ].map((report, i) => (
                                                    <div key={i} className="p-5 bg-white border border-[#E6E8EE] rounded-xl flex items-center justify-between hover:shadow-md transition-shadow">
                                                        <div className="flex items-center gap-3">
                                                            <Beaker className="text-[#0F766E]" size={20} />
                                                            <div>
                                                                <p className="text-sm font-bold text-[#1E2A5A]">{report.name}</p>
                                                                <p className="text-[10px] text-[#667085] uppercase">{report.date}</p>
                                                            </div>
                                                        </div>
                                                        <button className="text-xs font-bold text-[#0F766E] hover:underline">View</button>
                                                    </div>
                                                ))}
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>

                            {/* Quick Actions at Profile Level */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <button className="p-4 bg-white border border-[#E6E8EE] rounded-2xl flex flex-col items-center gap-2 hover:bg-[#CFF7F2] transition-all group">
                                    <FileText size={20} className="text-[#667085] group-hover:text-[#0F766E]" />
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-[#667085] group-hover:text-[#1E2A5A]">Add Notes</span>
                                </button>
                                <button className="p-4 bg-white border border-[#E6E8EE] rounded-2xl flex flex-col items-center gap-2 hover:bg-[#CFF7F2] transition-all group">
                                    <Clipboard size={20} className="text-[#667085] group-hover:text-[#0F766E]" />
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-[#667085] group-hover:text-[#1E2A5A]">Refer Patient</span>
                                </button>
                                <button className="p-4 bg-white border border-[#E6E8EE] rounded-2xl flex flex-col items-center gap-2 hover:bg-[#CFF7F2] transition-all group">
                                    <Beaker size={20} className="text-[#667085] group-hover:text-[#0F766E]" />
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-[#667085] group-hover:text-[#1E2A5A]">Request Lab</span>
                                </button>
                                <button className="p-4 bg-white border border-[#E6E8EE] rounded-2xl flex flex-col items-center gap-2 hover:bg-[#CFF7F2] transition-all group">
                                    <History size={20} className="text-[#667085] group-hover:text-[#0F766E]" />
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-[#667085] group-hover:text-[#1E2A5A]">Consult History</span>
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
}