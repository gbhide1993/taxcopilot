import { useEffect, useState } from "react";
import { Card, Row, Col, Table, Alert, Space } from "antd";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import "../styles/dashboard.css";

const Dashboard = () => {

  const navigate = useNavigate();

  const [stats, setStats] = useState({
    total_notices: 0,
    high_risk: 0,
    overdue: 0,
    unassigned: 0
  });

  const [deadlines, setDeadlines] = useState({
    overdue: 0,
    due_today: 0,
    due_3_days: 0,
    due_7_days: 0
  });

  const [sla, setSla] = useState({
    draft_pending: 0,
    review_pending: 0,
    submission_pending: 0,
    breached: 0
  });

  const [intelligence, setIntelligence] = useState({
    top_sections: [],
    top_clients: [],
    avg_resolution_days: 0
  });

  const [topClients, setTopClients] = useState([]);
  const [urgentNotices, setUrgentNotices] = useState([]);
  const [pipeline, setPipeline] = useState({});
  const [workload, setWorkload] = useState([]);
  const [clientRisk, setClientRisk] = useState([]);
  const [deadlineBoard, setDeadlineBoard] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDashboard = async () => {
    try {
      setLoading(true);

      const res = await api.get("/dashboard/");
      const d = res.data || {};

      setStats({
        total_notices: d.total_notices || 0,
        high_risk: d.high_risk || 0,
        overdue: d.overdue || 0,
        unassigned: d.unassigned || 0
      });

      setTopClients(d.top_clients || []);
      setUrgentNotices(d.urgent_notices || []);
      setPipeline(d.pipeline || {});
      setWorkload(d.workload || []);
      setClientRisk(d.client_risk || []);
      setDeadlineBoard(d.deadline_board || []);

    } catch (err) {
      console.error("Dashboard load failed", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDeadlines = async () => {
    try {
      const res = await api.get("/deadlines/");
      setDeadlines(res.data || {});
    } catch (err) {
      console.error("Deadline monitor failed", err);
    }
  };

  const fetchSLA = async () => {
    try {
      const res = await api.get("/sla/monitor");
      setSla(res.data || {});
    } catch (err) {
      console.error("SLA monitor failed", err);
    }
  };

  const fetchIntelligence = async () => {
    try {
      const res = await api.get("/intelligence/");
      setIntelligence(res.data || {});
    } catch (err) {
      console.error("Intelligence load failed", err);
    }
  };

  const generateAlerts = () => {

    const list = [];

    if (deadlines.overdue > 0)
      list.push(`⚠ ${deadlines.overdue} notices overdue`);

    if (deadlines.due_today > 0)
      list.push(`⚠ ${deadlines.due_today} notices due today`);

    if (sla.breached > 0)
      list.push(`⚠ ${sla.breached} SLA breaches`);

    if (stats.unassigned > 0)
      list.push(`⚠ ${stats.unassigned} notices unassigned`);

    setAlerts(list);

  };

  useEffect(() => {

    fetchDashboard();
    fetchDeadlines();
    fetchSLA();
    fetchIntelligence();

  }, []);

  useEffect(() => {

    generateAlerts();

  }, [deadlines, sla, stats]);

  const clientColumns = [
    { title: "Client", dataIndex: "client" },
    { title: "Notices", dataIndex: "count" }
  ];

  const workloadColumns = [
    { title: "CA", dataIndex: "ca" },
    { title: "Open Notices", dataIndex: "count" }
  ];

  const riskColumns = [
    { title: "Client", dataIndex: "client" },
    { title: "Notices", dataIndex: "notices" },
    { title: "Critical", dataIndex: "critical" },
    { title: "High", dataIndex: "high" },
    { title: "Medium", dataIndex: "medium" },
    { title: "Low", dataIndex: "low" }
  ];

  const deadlineColumns = [
    { title: "Client", dataIndex: "client" },
    { title: "Notice", dataIndex: "notice_number" },
    { title: "Section", dataIndex: "section" },
    { title: "Due Date", dataIndex: "due" }
  ];

  return (

    <div className="page-container">

      {alerts.length > 0 && (

        <Space direction="vertical" style={{ width:"100%", marginBottom:20 }}>

          {alerts.map((a, i) => (
            <Alert
              key={i}
              message={a}
              type="warning"
              showIcon
            />
          ))}

        </Space>

      )}

      {/* Litigation Intelligence (TOP) */}
      <div className="dashboard-section-title">
  Litigation Intelligence
</div>

<Row gutter={16} style={{ marginBottom:20 }}>

  {/* Most Litigated Sections */}

  <Col span={8}>
    <Card className="app-card">

      <div className="intel-title">
        Most Litigated Sections
      </div>

      <div className="app-table">

        {intelligence.top_sections?.map((s,i)=>(

          <div key={i} className="intel-row"
          onClick={()=>navigate(`/notices?section=${s.section}`)}>

            <div className="intel-name">
              {s.section || "Unknown Section"}
            </div>

            <div className="intel-value">
              {s.count}
            </div>

          </div>

        ))}

      </div>

    </Card>
  </Col>


  {/* Clients Generating Notices */}

  <Col span={8}>
    <Card className="app-card">

      <div className="intel-title">
        Clients Generating Notices
      </div>

      <div className="app-table">

        {intelligence.top_clients?.map((c,i)=>(

          <div key={i} className="intel-row"
         onClick={()=>navigate(`/clients?name=${c.client}`)}>

            <div className="intel-name">
              {c.client}
            </div>

            <div className="intel-value">
              {c.count}
            </div>

          </div>

        ))}

      </div>

    </Card>
  </Col>


  {/* Resolution Time */}

<Col span={8}>
  <Card
    className="app-card intel-card clickable-card"
    onClick={()=>navigate("/risk-monitor")}
  >

    <div className="intel-title">
      Litigation Resolution Time
    </div>

    <div className="intel-big-number">
      {intelligence.avg_resolution_days || 0} days
    </div>

    <div className="intel-hint">
      View delayed matters →
    </div>

  </Card>
</Col>

</Row>

      {/* Risk Monitor */}

      <div className="dashboard-section-title">
        Risk Monitor
      </div>

      <Row gutter={16} style={{ marginBottom:20 }}>

        <Col span={6}>
          <Card hoverable className="dashboard-card"
            onClick={() => navigate("/notices")}>
            Total Active
            <div className="metric-number metric-blue">
              {stats.total_notices}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card hoverable className="dashboard-card"
            onClick={() => navigate("/notices?risk_level=high")}>
            High Risk
            <div className="metric-number metric-orange">
              {stats.high_risk}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card hoverable className="dashboard-card"
            onClick={() => navigate("/notices?overdue_only=true")}>
            Overdue
            <div className="metric-number metric-red">
              {stats.overdue}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card hoverable className="dashboard-card"
            onClick={() => navigate("/notices?unassigned_only=true")}>
            Unassigned
            <div className="metric-number metric-purple">
              {stats.unassigned}
            </div>
          </Card>
        </Col>

      </Row>

      {/* Deadline Radar */}

      <div className="dashboard-section-title">
        Deadline Radar
      </div>

      <Row gutter={16} style={{ marginBottom:20 }}>

        <Col span={6}>
          <Card className="dashboard-card">
            Overdue
            <div className="metric-number metric-red">
              {deadlines.overdue}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card className="dashboard-card">
            Due Today
            <div className="metric-number metric-orange">
              {deadlines.due_today}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card className="dashboard-card">
            Due in 3 Days
            <div className="metric-number metric-blue">
              {deadlines.due_3_days}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card className="dashboard-card">
            Due in 7 Days
            <div className="metric-number metric-blue">
              {deadlines.due_7_days}
            </div>
          </Card>
        </Col>

      </Row>

      {/* SLA Monitor */}

      <div className="dashboard-section-title">
        SLA Monitor
      </div>

      <Row gutter={16} style={{ marginBottom:20 }}>

        <Col span={6}>
          <Card className="dashboard-card">
            Draft Pending
            <div className="metric-number">
              {sla.draft_pending}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card className="dashboard-card">
            Review Pending
            <div className="metric-number">
              {sla.review_pending}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card className="dashboard-card">
            Submission Pending
            <div className="metric-number">
              {sla.submission_pending}
            </div>
          </Card>
        </Col>

        <Col span={6}>
          <Card className="dashboard-card">
            SLA Breached
            <div className="metric-number metric-red">
              {sla.breached}
            </div>
          </Card>
        </Col>

      </Row>

      {/* Deadline Board */}

      <Card title="Next 7 Day Deadline Board" className="dashboard-table-card">

        <div className="app-table">
        <Table
          rowKey="id"
          columns={deadlineColumns}
          dataSource={deadlineBoard}
          pagination={false}
          size="small"
          onRow={(record) => ({
            onClick: () => navigate(`/notices/${record.id}`)
          })}
        />
        </div>

      </Card>

      {/* Client Risk */}

      <Card
        title="Client Risk Heat Table"
        className="dashboard-table-card"
        style={{ marginTop:20 }}>

        <div className="app-table">    
        <Table
          rowKey="client"
          columns={riskColumns}
          dataSource={clientRisk}
          pagination={false}
          size="small"
        />
        </div>

      </Card>

      <Row gutter={16} style={{ marginTop:20 }}>

        <Col span={12}>

          <Card title="Top Clients by Notices"
            className="dashboard-table-card">

            <div className="app-table">    
            <Table
              rowKey="client"
              columns={clientColumns}
              dataSource={topClients}
              pagination={false}
              size="small"
            />
            </div>

          </Card>

        </Col>

        <Col span={12}>

          <Card title="Team Workload"
            className="dashboard-table-card">

            <div className="app-table">
            <Table
              rowKey="ca"
              columns={workloadColumns}
              dataSource={workload}
              pagination={false}
              size="small"
            />
            </div>

          </Card>

        </Col>

      </Row>

    </div>

  );

};

export default Dashboard;