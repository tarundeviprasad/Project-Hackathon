import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PatientLogin from './Patientlogin';
import DoctorLogin from './Doctorlogin';
import AdminLogin from './Adminlogin';
import DoctorPortal from './Doctorportal';
import React, { useState } from 'react';
import {
  Activity, Stethoscope, User, Hospital, Shield, Globe, Bell,
  Headset, HelpCircle, ChevronDown, ArrowRight, ArrowRightLeft,
  Search, MapPin, Calendar, FileText, Smartphone,
  Menu, X, CheckCircle2, LayoutDashboard, HeartPulse, AlertCircle, Phone, UserCheck
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- CONFIGURATION ---
const PORTAL_ROUTES = {
  patient: "/patient-login",
  doctor: "/doctor-login",
  admin: "/admin-login"
};

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

// --- TRANSLATIONS ---
const translations = {
  en: {
    heroBadge: 'National Health Gateway',
    heroHeading1: 'Connecting Communities to',
    heroHeading2: 'Accessible Healthcare',
    heroDesc: 'AarogyaConnect is a centralized digital healthcare platform designed to bridge the gap between rural patients, doctors, and specialists through technology.',
    exploreBtn: 'Explore Healthcare Services',
    choosePortalBtn: 'Choose Your Portal',
    servicesTitle: 'Professional Healthcare Ecosystem',
    servicesDesc: 'Advanced digital infrastructure optimized for rural healthcare delivery and longitudinal patient care management.',
    service1: { title: 'Intelligent Facility Mapping', desc: 'Utilizing geospatial intelligence to provide real-time visibility into the nearest verified Primary Health Centres and specialized clinics, ensuring immediate care.' },
    service2: { title: 'Specialist Gateway', desc: 'Bridging the urban-rural divide by facilitating direct encrypted access to board-certified medical specialists for high-fidelity clinical diagnosis.' },
    service3: { title: 'Live Resource Analytics', desc: 'An innovative dashboard providing real-time data on bed availability and life-saving equipment at regional hubs to optimize patient inflow.' },
    service4: { title: 'Integrated Referral Pathway', desc: 'A frictionless end-to-end clinical workflow that automates medical data transfer and prioritizes emergency cases within the tertiary network.' },
    service5: { title: 'Smart Appointment Engine', desc: 'Eliminating physical queues through an intuitive, low-latency scheduling module that supports regional language inputs and minimizes wait times.' },
    service6: { title: 'Unified Digital Records', desc: 'A secure, longitudinal patient data repository enabling healthcare providers to access comprehensive clinical histories for rapid decision-making.' },
    service7: { title: 'Virtual Clinical Outreach', desc: 'Leveraging low-bandwidth optimized video technology to deliver tele-health consultations directly to underserved rural communities.' },
    service8: { title: 'Emergency Sync Protocols', desc: 'Synchronizing regional ambulance dispatch with GPS coordinates and trauma-unit readiness to drastically reduce critical response times.' },
    portalTitle: 'Secure Gateway Access',
    portalDesc: 'Authorized portal access for Patients, Medical Practitioners, and Administrative Officers.',
    patientPortal: 'Patient Portal',
    patientPortalDesc: 'Access healthcare services, book appointments, and view personal clinical records.',
    doctorPortal: 'Doctor Portal',
    doctorPortalDesc: 'Manage patient consultations, diagnostics, and specialist referrals efficiently.',
    adminPortal: 'Admin Portal',
    adminPortalDesc: 'Administrative oversight of healthcare facilities and regional operations.',
    loginBtn: 'Login',
    supportTitle: 'Help & Support Center',
    supportDesc: 'Dedicated assistance for the AarogyaConnect healthcare ecosystem.',
    clinicalSupport: 'Clinical Support',
    clinicalSupportDesc: 'Facing technical difficulties with the portal? Our specialized team is available for platform guidance.',
    contactSupport: 'Contact Support',
    userDocs: 'User Documentation',
    userDocsDesc: 'Review our comprehensive FAQs on registration, specialist referrals, and clinical data security.',
    viewDocs: 'View Documentation',
    home: 'Home',
    doctorPortalNav: 'Doctor Portal',
    patientPortalNav: 'Patient Portal',
    support: 'Customer Service',
    faqs: 'Help & FAQs',
    emergency: 'Emergency Response',
    emergencyNumber: '108',
    headerTitle: 'Healthcare Gateway Platform',
    nationalPortal: 'National Health Portal',
    adminPortalNav: 'Admin Portal',
  },
  hi: {
    heroBadge: 'राष्ट्रीय स्वास्थ्य गेटवे',
    heroHeading1: 'समुदायों को जोड़ना',
    heroHeading2: 'सुलभ स्वास्थ्यसेवा',
    heroDesc: 'आरोग्य कनेक्ट एक केंद्रीकृत डिजिटल स्वास्थ्य सेवा मंच है जो ग्रामीण रोगियों, डॉक्टरों और विशेषज्ञों को प्रौद्योगिकी के माध्यम से जोड़ता है।',
    exploreBtn: 'स्वास्थ्यसेवा सेवाएँ खोजें',
    choosePortalBtn: 'अपना पोर्टल चुनें',
    servicesTitle: 'पेशेवर स्वास्थ्यसेवा पारिस्थितिकी तंत्र',
    servicesDesc: 'ग्रामीण स्वास्थ्य सेवा वितरण के लिए अनुकूलित उन्नत डिजिटल बुनियादी ढांचा।',
    service1: { title: 'बुद्धिमान सुविधा मानचित्रण', desc: 'भौगोलिक बुद्धिमत्ता का उपयोग करके निकटतम प्राथमिक स्वास्थ्य केंद्र की वास्तविक समय दृश्यता प्रदान करें।' },
    service2: { title: 'विशेषज्ञ गेटवे', desc: 'शहरी-ग्रामीण विभाजन को कम करें और प्रमाणित चिकित्सा विशेषज्ञों के साथ सीधी पहुंच सुविधाजनक बनाएं।' },
    service3: { title: 'लाइव संसाधन विश्लेषण', desc: 'बिस्तर की उपलब्धता और जीवन रक्षक उपकरणों के लिए वास्तविक समय डेटा प्रदान करें।' },
    service4: { title: 'एकीकृत रेफरल पथ', desc: 'चिकित्सा डेटा हस्तांतरण को स्वचालित करें और आपातकालीन मामलों को प्राथमिकता दें।' },
    service5: { title: 'स्मार्ट नियुक्ति इंजन', desc: 'क्षेत्रीय भाषा इनपुट का समर्थन करने वाला कम विलंब वाला शेड्यूलिंग मॉड्यूल।' },
    service6: { title: 'एकीकृत डिजिटल रिकॉर्ड', desc: 'स्वास्थ्य सेवा प्रदाताओं को व्यापक नैदानिक इतिहास तक सुरक्षित पहुंच प्रदान करें।' },
    service7: { title: 'वर्चुअल क्लिनिकल आउटरीच', desc: 'कम बैंडविड्थ वीडियो तकनीक का उपयोग करके ग्रामीण इलाकों को दूरवर्ती स्वास्थ्य सेवा प्रदान करें।' },
    service8: { title: 'आपातकालीन सिंक प्रोटोकॉल', desc: 'क्षेत्रीय एम्बुलेंस डिस्पैच को जीपीएस समन्वय के साथ सिंक करें।' },
    portalTitle: 'सुरक्षित गेटवे पहुंच',
    portalDesc: 'रोगियों, चिकित्सकों और प्रशासनिक अधिकारियों के लिए अधिकृत पोर्टल पहुंच।',
    patientPortal: 'रोगी पोर्टल',
    patientPortalDesc: 'स्वास्थ्य सेवाओं तक पहुंचें, नियुक्तियां बुक करें और व्यक्तिगत नैदानिक रिकॉर्ड देखें।',
    doctorPortal: 'डॉक्टर पोर्टल',
    doctorPortalDesc: 'रोगी परामर्श, नैदानिक और विशेषज्ञ रेफरल को कुशलतापूर्वक प्रबंधित करें।',
    adminPortal: 'प्रशासन पोर्टल',
    adminPortalDesc: 'स्वास्थ्य सुविधाओं और क्षेत्रीय संचालन का प्रशासनिक पर्यवेक्षण।',
    loginBtn: 'लॉगिन करें',
    supportTitle: 'सहायता और सहायता केंद्र',
    supportDesc: 'आरोग्य कनेक्ट स्वास्थ्यसेवा पारिस्थितिकी तंत्र के लिए समर्पित सहायता।',
    clinicalSupport: 'नैदानिक सहायता',
    clinicalSupportDesc: 'पोर्टल में तकनीकी कठिनाई का सामना कर रहे हैं? हमारी विशेष टीम प्लेटफॉर्म मार्गदर्शन के लिए उपलब्ध है।',
    contactSupport: 'सहायता से संपर्क करें',
    userDocs: 'उपयोगकर्ता दस्तावेज',
    userDocsDesc: 'पंजीकरण, विशेषज्ञ रेफरल और नैदानिक डेटा सुरक्षा पर व्यापक FAQs देखें।',
    viewDocs: 'दस्तावेज़ देखें',
    home: 'होम',
    doctorPortalNav: 'डॉक्टर पोर्टल',
    patientPortalNav: 'रोगी पोर्टल',
    support: 'ग्राहक सेवा',
    faqs: 'सहायता और FAQ',
    emergency: 'आपातकालीन प्रतिक्रिया',
    emergencyNumber: '108',
    headerTitle: 'स्वास्थ्य गेटवे मंच',
    nationalPortal: 'राष्ट्रीय स्वास्थ्य पोर्टल',
    adminPortalNav: 'प्रशासन पोर्टल',
  },
  te: {
    heroBadge: 'జాతీయ ఆరోగ్య గేటువే',
    heroHeading1: 'సమాజాలను అనుసంధానం చేయడం',
    heroHeading2: 'సుందరమైన ఆరోగ్య సేవ',
    heroDesc: 'ఆరోగ్య కనెక్ట్ ఒక కేంద్రీకృత డిజిటల్ ఆరోగ్య సేవ వేదిక, ఇది గ్రామీణ రోగులు, డాక్టర్లు మరియు ఆరోగ్య నిపుణులను సంযోగం చేస్తుంది.',
    exploreBtn: 'ఆరోగ్య సేవలను అన్వేషించండి',
    choosePortalBtn: 'మీ పోర్టల్‌ను ఎంచుకోండి',
    servicesTitle: 'ప్రొఫెషనల్ ఆరోగ్య సేవ ఈకోసిస్టమ్',
    servicesDesc: 'గ్రామీణ ఆరోగ్య సేవ పంపిణీ కోసం ఆప్టిమైజ్ చేసిన అధునాతన డిజిటల్ సదుపాయం.',
    service1: { title: 'తెలివైన సదుపాయ మ్యాపింగ్', desc: 'భౌగోళిక నిధానతను ఉపయోగించి ఆ కాబట్టి అత్యంత సమీప ప్రాథమిక ఆరోగ్య కేంద్రాలను చూపించండి.' },
    service2: { title: 'వైద్య నిపుణుల గేటువే', desc: 'నగర-గ్రామీణ విభజనను తగ్గించండి మరియు ధృవీకృత వైద్య నిపుణులకు ప్రత్యక్ష ప్రాప్తిని సులభతరం చేయండి.' },
    service3: { title: 'లైవ్ వనరుల విశ్లేషణ', desc: 'మంచం యొక్క లభ్యత మరియు జీవన రక్షక సాధనాల కోసం నిజ సమయ డేటాను అందించండి.' },
    service4: { title: 'సమన్వయ సూచన మార్గం', desc: 'వైద్య డేటా బదిలీని స్వయంచాలకంగా చేయండి మరియు అత్యవసర కేసులకు ప్రాధాన్యతను ఇవ్వండి.' },
    service5: { title: 'స్మార్ట్ నియామక ఇంజిన్', desc: 'ప్రాంతీయ భాష ఇన్‌పుట్‌కు సమర్థన చేసే తక్కువ ఆలస్యం షెడ్యూలింగ్ మాడ్యూల్.' },
    service6: { title: 'సమన్వయ డిజిటల్ రికార్డ్‌లు', desc: 'ఆరోగ్య సేవ ప్రదాతలకు సమగ్ర క్లినికల్ చరిత్ర కు నిరాপద ప్రాప్తిని అందించండి.' },
    service7: { title: 'వర్చువల్ క్లినికల్ అవుట్‌రీచ్', desc: 'తక్కువ బ్యాండుబిడ్ విడియో సాంకేతికతను ఉపయోగించి గ్రామీణ ప్రాంతాలకు టెలిహెల్త్ సేవలను అందించండి.' },
    service8: { title: 'అత్యవసర సింక్ ప్రోటోకాల్‌లు', desc: 'ప్రాంతీయ యాంబులెన్స్ డిస్‌పాచ్‌ను జीపిఎస్ కోఆర్డినేట్‌లతో సింక్ చేయండి.' },
    portalTitle: 'సురక్షిత గేటువే ప్రవేశం',
    portalDesc: 'రోగులు, వైద్య నిపుణులు మరియు నిర్వాహక అధికారుల కోసం అధికృత పోర్టల్ ప్రవేశం.',
    patientPortal: 'రోగి పోర్టల్',
    patientPortalDesc: 'ఆరోగ్య సేవలను ప్రవేశించండి, నియామకాలను బుక్ చేయండి మరియు వ్యక్తిగత క్లినికల్ రికార్డ్‌లను చూడండి.',
    doctorPortal: 'డాక్టర్ పోర్టల్',
    doctorPortalDesc: 'రోగి సంప్రదింపులు, నిరూపణ మరియు వైద్య నిపుణుల సూచన నిర్వహించండి.',
    adminPortal: 'నిర్వాహక పోర్టల్',
    adminPortalDesc: 'ఆరోగ్య సదుపాయాలు మరియు ప్రాంతీయ కార్యకలాపాల యొక్క నిర్వాహక నిరీక్షణ.',
    loginBtn: 'లాగిన్',
    supportTitle: 'సహాయ మరియు సపోర్ట్ సెంటర్',
    supportDesc: 'ఆరోగ్య కనెక్ట్ ఆరోగ్య సేవ ఈకోసిస్టమ్‌కు నిబద్ధ సహాయం.',
    clinicalSupport: 'క్లినికల్ సపోర్ట్',
    clinicalSupportDesc: 'పోర్టల్‌లో సాంకేతిక సమస్యలను ఎదుర్కొంటున్నారా? మా ప్రత్యేక బృందం వేదిక మార్గదర్శకం కోసం అందుబాటులో ఉంది.',
    contactSupport: 'సపోర్ట్‌ను సంప్రదించండి',
    userDocs: 'వినియోగదారు డాక్యుమెంటేషన్',
    userDocsDesc: 'నమోదు, వైద్య నిపుణుల సూచన మరియు క్లినికల్ డేటా భద్రతపై సమగ్ర FAQలను చూడండి.',
    viewDocs: 'డాక్యుమెంటేషన్‌ను చూడండి',
    home: 'హోమ్',
    doctorPortalNav: 'డాక్టర్ పోర్టల్',
    patientPortalNav: 'రోగి పోర్టల్',
    support: 'కస్టమర్ సేవ',
    faqs: 'సహాయ మరియు FAQ',
    emergency: 'అత్యవసర ప్రతిక్రియ',
    emergencyNumber: '108',
    headerTitle: 'ఆరోగ్య గేటువే వేదిక',
    nationalPortal: 'జాతీయ ఆరోగ్య పోర్టల్',
    adminPortalNav: 'నిర్వాహక పోర్టల్',
  },
  mr: {
    heroBadge: 'राष्ट्रीय आरोग्य गेटवे',
    heroHeading1: 'समुदायांना जोडणे',
    heroHeading2: 'सुलभ स्वास्थ्यसेवा',
    heroDesc: 'आरोग्य कनेक्ट एक केंद्रीकृत डिजिटल आरोग्य सेवा मंच आहे जो ग्रामीण रोगी, डॉक्टर आणि तज्ञांना तंत्रज्ञानाद्वारे जोडतो.',
    exploreBtn: 'आरोग्य सेवा एक्सप्लोर करा',
    choosePortalBtn: 'आपले पोर्टल निवडा',
    servicesTitle: 'व्यावसायिक आरोग्य सेवा पारिस्थितिकी तंत्र',
    servicesDesc: 'ग्रामीण आरोग्य सेवा वितरणासाठी अनुकूलित प्रगत डिजिटल अवसंरचना.',
    service1: { title: 'बुद्धिमान सुविधा मानचित्रण', desc: 'भौगोलिक बुद्धिमत्ता वापरून जवळच्या प्राथमिक आरोग्य केंद्रांचे वास्तविक समय दृश्य प्रदान करा.' },
    service2: { title: 'तज्ञ गेटवे', desc: 'शहर-गावठी विभाजन कमी करा आणि प्रमाणित वैद्यकीय तज्ञांचे थेट प्रवेश सुलभ करा.' },
    service3: { title: 'लाइव संसाधन विश्लेषण', desc: 'बेडची उपलब्धता आणि जीवन रक्षक उपकरणांसाठी वास्तविक समय डेटा प्रदान करा.' },
    service4: { title: 'एकीकृत संदर्भ मार्ग', desc: 'वैद्यकीय डेटा हस्तांतरण स्वयंचलित करा आणि आपातकालीन प्रकरणांना प्राधान्य द्या.' },
    service5: { title: 'स्मार्ट नियुक्ती इंजिन', desc: 'क्षेत्रीय भाषा इनपुटला समर्थन करणारे कम विलंब शेड्यूलिंग मॉड्यूल.' },
    service6: { title: 'एकीकृत डिजिटल रेकॉर्ड', desc: 'स्वास्थ्य सेवा प्रदाताओंना व्यापक क्लिनिकल इतिहासचा सुरक्षित प्रवेश प्रदान करा.' },
    service7: { title: 'व्हर्च्युअल क्लिनिकल आउटरीच', desc: 'कमी बँडविड्थ व्हिडिओ तंत्रज्ञान वापरून ग्रामीण भागांना टेलीहेल्थ सेवा प्रदान करा.' },
    service8: { title: 'आपातकालीन सिंक प्रोटोकॉल', desc: 'क्षेत्रीय अ‍ॅम्बुलन्स डिस्पॅच GPS निर्देशांकांसह सिंक करा.' },
    portalTitle: 'सुरक्षित गेटवे प्रवेश',
    portalDesc: 'रोगी, वैद्यकीय व्यावसायिक आणि प्रशासकीय अधिकारी साठी अधिकृत पोर्टल प्रवेश.',
    patientPortal: 'रोगी पोर्टल',
    patientPortalDesc: 'आरोग्य सेवा प्रवेश करा, नियुक्तीची बुकिंग करा आणि वैयक्तिक क्लिनिकल रेकॉर्ड पहा.',
    doctorPortal: 'डॉक्टर पोर्टल',
    doctorPortalDesc: 'रोगी सल्लामसलत, निदान आणि तज्ञ संदर्भ कुशलतेने व्यवस्थापित करा.',
    adminPortal: 'प्रशासकीय पोर्टल',
    adminPortalDesc: 'आरोग्य सुविधा आणि प्रादेशिक कार्यांचे प्रशासकीय देखरेख.',
    loginBtn: 'लॉगिन करा',
    supportTitle: 'मदत आणि समर्थन केंद्र',
    supportDesc: 'आरोग्य कनेक्ट आरोग्य सेवा पारिस्थितिकी तंत्रासाठी समर्पित सहायता.',
    clinicalSupport: 'क्लिनिकल समर्थन',
    clinicalSupportDesc: 'पोर्टलमध्ये तांत्रिक अडचणीला सामोरे जात आहात? आमची विशेष टीम मंच मार्गदर्शनासाठी उपलब्ध आहे.',
    contactSupport: 'समर्थनशी संपर्क साधा',
    userDocs: 'वापरकर्ता दस्तऐवज',
    userDocsDesc: 'नोंदणी, तज्ञ संदर्भ आणि क्लिनिकल डेटा सुरक्षेवर व्यापक FAQs पहा.',
    viewDocs: 'दस्तऐवज पहा',
    home: 'होम',
    doctorPortalNav: 'डॉक्टर पोर्टल',
    patientPortalNav: 'रोगी पोर्टल',
    support: 'ग्राहक सेवा',
    faqs: 'मदत आणि FAQ',
    emergency: 'आपातकालीन प्रतिक्रिया',
    emergencyNumber: '108',
    headerTitle: 'आरोग्य गेटवे मंच',
    nationalPortal: 'राष्ट्रीय आरोग्य पोर्टल',
    adminPortalNav: 'प्रशासकीय पोर्टल',
  }
};

// --- COMPONENTS ---

const LanguageSelector = ({ lang, onLangChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const languageMap = { 'en': 'English', 'hi': 'हिंदी', 'te': 'తెలుగు', 'mr': 'मराठी' };
  const languages = ['en', 'hi', 'te', 'mr'];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 border border-[#E6E8EE] rounded-lg hover:bg-gray-50 transition-colors"
      >
        <Globe size={18} className="text-[#0F766E]" />
        <span className="font-medium text-[#1E2A5A] text-sm">{languageMap[lang]}</span>
        <ChevronDown size={14} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
            className="absolute right-0 mt-2 w-32 bg-white border border-[#E6E8EE] rounded-xl shadow-xl z-50 overflow-hidden"
          >
            {languages.map((l) => (
              <button key={l} onClick={() => { onLangChange(l); setIsOpen(false); }}
                className="w-full text-left px-4 py-2.5 hover:bg-[#CFF7F2] transition-colors text-sm text-[#172033]"
              >
                {languageMap[l]}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// INNOVATIVE SERVICE CARD (No Explore Option)
const ServiceCard = ({ icon: Icon, title, desc }) => (
  <motion.div
    whileHover={{ y: -8 }}
    className="bg-white p-8 rounded-2xl border border-[#E6E8EE] shadow-sm hover:shadow-xl hover:border-[#0F766E]/30 transition-all group flex flex-col h-full"
  >
    <div className="w-14 h-14 bg-[#CFF7F2] rounded-2xl flex items-center justify-center mb-6 group-hover:bg-[#0F766E] transition-colors shadow-inner">
      <Icon className="text-[#0F766E] group-hover:text-white" size={28} />
    </div>
    <h3 className="text-xl font-bold text-[#1E2A5A] mb-4 tracking-tight">{title}</h3>
    <p className="text-[#667085] text-sm leading-relaxed font-medium">
      {desc}
    </p>
  </motion.div>
);

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-4 px-6 py-4 transition-all border-l-4 ${active
      ? 'bg-[#CFF7F2] border-[#0F766E] text-[#1E2A5A]'
      : 'bg-transparent border-transparent text-[#667085] hover:bg-gray-50'
      }`}
  >
    <Icon size={20} className={active ? 'text-[#0F766E]' : 'text-[#667085]'} />
    <span className={`font-medium ${active ? 'font-bold text-[#1E2A5A]' : ''}`}>{label}</span>
  </button>
);

// --- MAIN VIEWS ---

const HomeView = ({ lang, t }) => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-16 pb-20">
    {/* HERO SECTION */}
    <section className="bg-white rounded-3xl p-10 border border-[#E6E8EE] shadow-sm flex flex-col md:flex-row items-center gap-10">
      <div className="flex-1 space-y-6">
        <span className="px-4 py-1.5 bg-[#CFF7F2] text-[#0F766E] text-xs font-bold uppercase tracking-widest rounded-full">
          {t.heroBadge}
        </span>
        <h1 className="text-5xl font-bold text-[#1E2A5A] leading-tight">
          {t.heroHeading1} <span className="text-[#0F766E]">{t.heroHeading2}</span>
        </h1>
        <p className="text-[#667085] text-lg leading-relaxed max-w-xl">
          {t.heroDesc}
        </p>
        <div className="flex flex-wrap gap-4 pt-4">
          <button className="bg-[#0F766E] hover:bg-[#0d665f] text-white px-8 py-4 rounded-xl font-bold transition-all shadow-lg shadow-teal-900/10 flex items-center gap-2">
            {t.exploreBtn} <ArrowRight size={18} />
          </button>
          <button className="bg-white border-2 border-[#1E2A5A] text-[#1E2A5A] hover:bg-[#1E2A5A] hover:text-white px-8 py-4 rounded-xl font-bold transition-all">
            {t.choosePortalBtn}
          </button>
        </div>
      </div>
      <div className="flex-1 flex justify-center">
        <div className="relative w-full max-w-md aspect-square bg-[#F8F7F4] rounded-full flex items-center justify-center border border-[#E6E8EE]">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 50, repeat: Infinity, ease: "linear" }} className="absolute w-full h-full border-2 border-dashed border-[#CFF7F2] rounded-full" />
          <Activity size={120} className="text-[#0F766E] opacity-20" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="grid grid-cols-2 gap-8">
              {[User, Stethoscope, Hospital, Shield].map((Icn, i) => (
                <div key={i} className="p-4 bg-white rounded-2xl shadow-lg border border-[#E6E8EE] text-[#0F766E]">
                  <Icn size={32} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* INNOVATIVE SERVICES SECTION */}
    <section>
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-[#1E2A5A] mb-4">{t.servicesTitle}</h2>
        <p className="text-[#667085] max-w-2xl mx-auto">{t.servicesDesc}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ServiceCard icon={Search} title={t.service1.title} desc={t.service1.desc} />
        <ServiceCard icon={UserCheck} title={t.service2.title} desc={t.service2.desc} />
        <ServiceCard icon={MapPin} title={t.service3.title} desc={t.service3.desc} />
        <ServiceCard icon={ArrowRightLeft} title={t.service4.title} desc={t.service4.desc} />
        <ServiceCard icon={Calendar} title={t.service5.title} desc={t.service5.desc} />
        <ServiceCard icon={FileText} title={t.service6.title} desc={t.service6.desc} />
        <ServiceCard icon={Smartphone} title={t.service7.title} desc={t.service7.desc} />
        <ServiceCard icon={AlertCircle} title={t.service8.title} desc={t.service8.desc} />
      </div>
    </section>

    {/* PORTAL ACCESS SECTION */}
    <section className="py-12 border-t border-[#E6E8EE]">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-[#1E2A5A] mb-4">{t.portalTitle}</h2>
        <p className="text-[#667085]">{t.portalDesc}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {[
          { type: 'patient', portal: t.patientPortal, desc: t.patientPortalDesc, icon: User, route: PORTAL_ROUTES.patient },
          { type: 'doctor', portal: t.doctorPortal, desc: t.doctorPortalDesc, icon: Stethoscope, route: PORTAL_ROUTES.doctor },
          { type: 'admin', portal: t.adminPortal, desc: t.adminPortalDesc, icon: LayoutDashboard, route: PORTAL_ROUTES.admin },
        ].map((portal) => (
          <div key={portal.type} className="bg-white p-8 rounded-3xl border border-[#E6E8EE] flex flex-col items-center text-center shadow-sm">
            <div className="w-16 h-16 bg-[#F8F7F4] rounded-2xl flex items-center justify-center text-[#1E2A5A] mb-6">
              <portal.icon size={32} />
            </div>
            <h3 className="text-xl font-bold text-[#1E2A5A] mb-3">{portal.portal}</h3>
            <p className="text-sm text-[#667085] mb-8">{portal.desc}</p>
            <a
              href={portal.route}
              className="w-full py-3 bg-[#1E2A5A] text-white rounded-xl font-bold hover:bg-[#2a3b7a] transition-all flex items-center justify-center gap-2"
            >
              {t.loginBtn} <ArrowRight size={16} />
            </a>
          </div>
        ))}
      </div>
    </section>
  </motion.div>
);

const SupportView = ({ lang, t }) => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-4xl mx-auto space-y-10">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-[#1E2A5A] mb-4">{t.supportTitle}</h1>
      <p className="text-[#667085]">{t.supportDesc}</p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white p-8 rounded-3xl border border-[#E6E8EE] shadow-sm">
        <Headset size={40} className="text-[#0F766E] mb-6" />
        <h2 className="text-2xl font-bold text-[#1E2A5A] mb-4">{t.clinicalSupport}</h2>
        <p className="text-[#667085] mb-6 text-sm leading-relaxed">{t.clinicalSupportDesc}</p>
        <button className="w-full py-3 border-2 border-[#0F766E] text-[#0F766E] font-bold rounded-xl hover:bg-[#0F766E] hover:text-white transition-all">
          {t.contactSupport}
        </button>
      </div>
      <div className="bg-white p-8 rounded-3xl border border-[#E6E8EE] shadow-sm">
        <HelpCircle size={40} className="text-[#0F766E] mb-6" />
        <h2 className="text-2xl font-bold text-[#1E2A5A] mb-4">{t.userDocs}</h2>
        <p className="text-[#667085] mb-6 text-sm leading-relaxed">{t.userDocsDesc}</p>
        <button className="w-full py-3 border-2 border-[#0F766E] text-[#0F766E] font-bold rounded-xl hover:bg-[#0F766E] hover:text-white transition-all">
          {t.viewDocs}
        </button>
      </div>
    </div>
  </motion.div>
);

// --- MAIN APPLICATION LAYOUT ---

function Home() {
  const [activePage, setActivePage] = useState('Home');
  const [showNotifications, setShowNotifications] = useState(false);
  const [lang, setLang] = useState('en');
  const t = translations[lang];

  return (
    <div className="flex h-screen bg-[#F8F7F4] font-sans text-[#172033] overflow-hidden">

      {/* SIDEBAR */}
      <aside className="w-72 bg-white border-r border-[#E6E8EE] flex flex-col z-30 shadow-sm">
        <div className="p-8 flex items-center gap-3">
          <div className="w-10 h-10 bg-[#1E2A5A] rounded-xl flex items-center justify-center text-white shadow-lg">
            <HeartPulse size={24} />
          </div>
          <div>
            <h1 className="text-xl font-black text-[#1E2A5A] tracking-tight uppercase leading-none">Aarogya</h1>
            <p className="text-[10px] font-bold text-[#0F766E] tracking-[0.2em] uppercase">Connect</p>
          </div>
        </div>

        <nav className="flex-1 py-4 space-y-1">
          <SidebarItem icon={Activity} label={t.home} active={activePage === 'Home'} onClick={() => setActivePage('Home')} />
          <SidebarItem icon={Stethoscope} label={t.doctorPortalNav} active={activePage === 'Doctor'} onClick={() => window.location.href = PORTAL_ROUTES.doctor} />
          <SidebarItem icon={User} label={t.patientPortalNav} active={activePage === 'Patient'} onClick={() => window.location.href = PORTAL_ROUTES.patient} />

          <div className="px-8 pt-8 pb-4">
            <span className="text-[10px] font-black text-[#667085] tracking-[0.3em] uppercase">{t.support}</span>
          </div>

          <SidebarItem icon={Headset} label={t.support} active={activePage === 'Support'} onClick={() => setActivePage('Support')} />
          <SidebarItem icon={HelpCircle} label={t.faqs} active={activePage === 'FAQ'} onClick={() => setActivePage('Support')} />
        </nav>

        <div className="p-6 m-4 bg-[#1E2A5A] rounded-2xl text-white">
          <p className="text-xs font-bold opacity-60 mb-2">{t.emergency}</p>
          <div className="flex items-center gap-2 text-xl font-black">
            <Phone size={20} className="text-[#CFF7F2]" />
            <span>{t.emergencyNumber}</span>
          </div>
        </div>
      </aside>

      {/* HEADER & MAIN CONTENT */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-20 bg-white border-b border-[#E6E8EE] flex items-center justify-between px-10 z-20 shadow-sm">
          <div className="flex items-center gap-4">
            <h2 className="text-[#1E2A5A] font-bold text-sm tracking-wide uppercase">{t.headerTitle}</h2>
            <div className="h-4 w-[1px] bg-[#E6E8EE] mx-2"></div>
            <div className="flex items-center gap-2 text-[#667085] text-sm">
              <MapPin size={16} />
              <span>{t.nationalPortal}</span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <a href={PORTAL_ROUTES.admin} className="px-4 py-2 border-2 border-[#1E2A5A] text-[#1E2A5A] text-sm font-bold rounded-xl hover:bg-[#1E2A5A] hover:text-white transition-all flex items-center gap-2">
              <Shield size={16} /> {t.adminPortalNav}
            </a>
            <LanguageSelector lang={lang} onLangChange={setLang} />
            <button onClick={() => setShowNotifications(!showNotifications)} className="p-2.5 bg-[#F8F7F4] rounded-xl text-[#1E2A5A] hover:bg-[#E6E8EE] relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full"></span>
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-10">
          <div className="max-w-7xl mx-auto">
            {activePage === 'Home' && <HomeView lang={lang} t={t} />}
            {activePage === 'Support' && <SupportView lang={lang} t={t} />}
          </div>
        </main>
      </div>
    </div>
  );
}
export default function App() {
  return (
      <Routes>
        {/* Main Website */}
        <Route path="/" element={<Home />} />

        {/* Doctor Login */}
        <Route path="/doctor-login" element={<DoctorLogin />} />

        {/* Admin Login */}
        <Route path="/admin-login" element={<AdminLogin />} />

        {/* Patient Login */}
        <Route path="/patient-login" element={<PatientLogin />} />

        {/* Doctor Dashboard */}
        <Route path="/doctor-dashboard" element={<DoctorPortal />} />
      </Routes>
  );
}