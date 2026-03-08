import { useEffect, useState } from "react";
import { Card, Row, Col, Table } from "antd";
import api from "../api/axios";

const Dashboard = () => {

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

  const [topClients, setTopClients] = useState([]);
  const [urgentNotices, setUrgentNotices] = useState([]);
  const [pipeline, setPipeline] = useState({});
  const [workload, setWorkload] = useState([]);

  const [clientRisk, setClientRisk] = useState([]);
  const [deadlineBoard, setDeadlineBoard] = useState([]);

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
      setDeadlines(res.data);

    } catch (err) {

      console.error("Deadline monitor failed", err);

    }

  };

  useEffect(() => {
    fetchDashboard();
    fetchDeadlines();
  }, []);

  const clientColumns = [
    { title: "Client", dataIndex: "client", width: 300 },
    { title: "Notices", dataIndex: "count", width: 150 }
  ];

  const urgentColumns = [
    { title: "Client", dataIndex: "client" },
    { title: "Section", dataIndex: "section" },
    { title: "Risk", dataIndex: "risk" },
    { title: "Due", dataIndex: "due" }
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

    <div>

      {/* KPI ROW */}

      <Row gutter={16} style={{ marginBottom: 16 }}>

        <Col span={6}>
          <Card size="small">
            Total Active
            <h2>{stats.total_notices}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            High Risk
            <h2 style={{ color:"#fa8c16" }}>
              {stats.high_risk}
            </h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            Overdue
            <h2 style={{ color:"#ff4d4f" }}>
              {stats.overdue}
            </h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            Unassigned
            <h2>{stats.unassigned}</h2>
          </Card>
        </Col>

      </Row>


      {/* DEADLINE MONITOR */}

      <Row gutter={16} style={{ marginBottom: 16 }}>

        <Col span={6}>
          <Card size="small">
            Overdue
            <h2 style={{ color:"#ff4d4f" }}>{deadlines.overdue}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            Due Today
            <h2 style={{ color:"#fa8c16" }}>{deadlines.due_today}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            Due in 3 Days
            <h2>{deadlines.due_3_days}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            Due in 7 Days
            <h2>{deadlines.due_7_days}</h2>
          </Card>
        </Col>

      </Row>


      {/* TOP CLIENTS */}

      <Card title="Top Clients by Notices" style={{ marginBottom: 16 }}>

        <Table
          rowKey="client"
          columns={clientColumns}
          dataSource={topClients}
          loading={loading}
          pagination={false}
          size="small"
        />

      </Card>


      {/* URGENT NOTICES */}

      <Card title="Urgent Notices" style={{ marginBottom: 16 }}>

        <Table
          rowKey="id"
          columns={urgentColumns}
          dataSource={urgentNotices}
          pagination={false}
          size="small"
        />

      </Card>


      {/* CLIENT RISK HEAT TABLE */}

      <Card title="Client Risk Heat Table" style={{ marginBottom: 16 }}>

        <Table
          rowKey="client"
          columns={riskColumns}
          dataSource={clientRisk}
          pagination={false}
          size="small"
        />

      </Card>


      {/* DEADLINE BOARD */}

      <Card title="Next 7 Day Deadline Board" style={{ marginBottom: 16 }}>

        <Table
          rowKey="id"
          columns={deadlineColumns}
          dataSource={deadlineBoard}
          pagination={false}
          size="small"
        />

      </Card>


      {/* PIPELINE + WORKLOAD */}

      <Row gutter={16}>

        <Col span={12}>

          <Card title="Pipeline Status" size="small">

            <div style={{ display:"flex", justifyContent:"space-between" }}>

              <div>
                Open<br/>
                <b>{pipeline.open || 0}</b>
              </div>

              <div>
                In Progress<br/>
                <b>{pipeline.in_progress || 0}</b>
              </div>

              <div>
                Replied<br/>
                <b>{pipeline.replied || 0}</b>
              </div>

              <div>
                Closed<br/>
                <b>{pipeline.closed || 0}</b>
              </div>

            </div>

          </Card>

        </Col>


        <Col span={12}>

          <Card title="Team Workload" size="small">

            <Table
              rowKey="ca"
              columns={workloadColumns}
              dataSource={workload}
              pagination={false}
              size="small"
            />

          </Card>

        </Col>

      </Row>

    </div>

  );

};

export default Dashboard;