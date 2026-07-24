import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { ResetPassword } from "./pages/ResetPassword";
import { Dashboard } from "./pages/Dashboard";
import { Jobs } from "./pages/Jobs";
import { JobDetail } from "./pages/JobDetail";
import { Applications } from "./pages/Applications";
import { ApplicationAgent } from "./pages/ApplicationAgent";
import { Profile } from "./pages/Profile";
import { AtsAnalyzer } from "./pages/AtsAnalyzer";
import { Notifications } from "./pages/Notifications";
import { WhatsAppPairing } from "./pages/WhatsAppPairing";
import { Radar } from "./pages/Radar";
import { SkillGap } from "./pages/SkillGap";
import { Analytics } from "./pages/Analytics";
import { Automation } from "./pages/Automation";
import { Landing } from "./pages/Landing";
import { Demo } from "./pages/Demo";
import { LinkedInAnalyzer, PrivateLinkedInAnalyzer } from "./pages/LinkedInAnalyzer";
import { ApplymizeFit } from "./pages/ApplymizeFit";
import { Pricing } from "./pages/Pricing";
import { Billing } from "./pages/Billing";
import { AdminAnalytics } from "./pages/AdminAnalytics";
import { RecruiterPanel } from "./pages/RecruiterPanel";
import { AdvancedCV } from "./pages/AdvancedCV";
import { HowItWorks } from "./pages/HowItWorks";
import { PublicAtsLab } from "./pages/PublicAtsLab";

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/" element={<Landing />} />
            <Route path="/demo" element={<Demo />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/linkedin-analyzer" element={<LinkedInAnalyzer />} />
            <Route path="/como-funciona" element={<HowItWorks />} />
            <Route path="/laboratorio-ats" element={<PublicAtsLab />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/jobs/:jobId" element={<JobDetail />} />
                <Route path="/applications" element={<Applications />} />
              <Route path="/application-agent" element={<ApplicationAgent />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/ats-analyzer" element={<AtsAnalyzer />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/skill-gap" element={<SkillGap />} />
              <Route path="/radar" element={<Radar />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/automation" element={<Automation />} />
              <Route path="/whatsapp-pairing" element={<WhatsAppPairing />} />
              <Route path="/app/linkedin-analyzer" element={<PrivateLinkedInAnalyzer />} />
              <Route path="/applymize-fit" element={<ApplymizeFit />} />
              <Route path="/billing" element={<Billing />} />
              <Route path="/admin" element={<AdminAnalytics />} />
              <Route path="/recruiter" element={<RecruiterPanel />} />
              <Route path="/cv-pro" element={<AdvancedCV />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
