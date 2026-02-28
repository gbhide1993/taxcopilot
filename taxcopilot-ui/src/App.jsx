import { Layout, Menu } from "antd";
import {
  DashboardOutlined,
  FileTextOutlined,
  TeamOutlined,
  EditOutlined,
  AuditOutlined,
  WarningOutlined,
  BarChartOutlined,
  SettingOutlined,
} from "@ant-design/icons";

import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Notices from "./pages/Notices";
import Clients from "./pages/Clients";
import Drafts from "./pages/Drafts";
import Appeals from "./pages/Appeals";
import RiskMonitor from "./pages/RiskMonitor";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

const { Header, Sider, Content } = Layout;

const LayoutWrapper = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        theme="light"
        width={220}
        style={{ borderRight: "1px solid #f0f0f0" }}
      >
        <div style={{ padding: 16, fontWeight: 600, fontSize: 16 }}>
          TaxCopilot
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          onClick={(e) => navigate(e.key)}
          items={[
            { key: "/", icon: <DashboardOutlined />, label: "Dashboard" },
            { key: "/notices", icon: <FileTextOutlined />, label: "Notices" },
            { key: "/clients", icon: <TeamOutlined />, label: "Clients" },
            { key: "/drafts", icon: <EditOutlined />, label: "Drafts" },
            { key: "/appeals", icon: <AuditOutlined />, label: "Appeals" },
            { key: "/risk", icon: <WarningOutlined />, label: "Risk Monitor" },
            { key: "/reports", icon: <BarChartOutlined />, label: "Reports" },
            { key: "/settings", icon: <SettingOutlined />, label: "Settings" },
          ]}
        />
      </Sider>

      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 16px",
            borderBottom: "1px solid #f0f0f0",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ fontWeight: 500 }}>TaxCopilot Enterprise</div>
          <div>Firm License: Active</div>
        </Header>

        <Content style={{ padding: 16, background: "#ffffff" }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/notices" element={<Notices />} />
            <Route path="/clients" element={<Clients />} />
            <Route path="/drafts" element={<Drafts />} />
            <Route path="/appeals" element={<Appeals />} />
            <Route path="/risk" element={<RiskMonitor />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

function App() {
  return (
    <BrowserRouter>
      <LayoutWrapper />
    </BrowserRouter>
  );
}

export default App;