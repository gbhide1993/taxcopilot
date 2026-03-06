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

  const [topClients, setTopClients] = useState([]);
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

    } catch (err) {

      console.error("Dashboard load failed", err);

    } finally {

      setLoading(false);

    }

  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const columns = [

    {
      title: "Client",
      dataIndex: "client",
      width: 300
    },

    {
      title: "Notices",
      dataIndex: "count",
      width: 150
    }

  ];

  return (

    <div>

      {/* KPI Cards */}

      <Row gutter={16} style={{ marginBottom: 20 }}>

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

      {/* Top Clients */}

      <Card title="Top Clients by Notices">

        <Table
          rowKey="client"
          columns={columns}
          dataSource={topClients}
          loading={loading}
          pagination={false}
        />

      </Card>

    </div>

  );

};

export default Dashboard;