import { Card, Row, Col, Table, Tag } from "antd";
import { useEffect, useState } from "react";
import api from "../api/axios";
import dayjs from "dayjs";

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [topNotices, setTopNotices] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await api.get("/risk/monitor");

      setStats(res.data);

      setTopNotices(
        (res.data.top_notices || []).map((item) => ({
          key: item.notice_id,
          notice: item.notice_number,
          dueDate: item.due_date
            ? dayjs(item.due_date).format("DD MMM YYYY")
            : "—",
          risk: item.risk_score,
        }))
      );
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: "Notice Number", dataIndex: "notice" },
    { title: "Due Date", dataIndex: "dueDate" },
    {
      title: "Risk Score",
      dataIndex: "risk",
      render: (risk) => {
        if (risk >= 4) return <Tag color="red">{risk.toFixed(2)}</Tag>;
        if (risk >= 2.5) return <Tag color="orange">{risk.toFixed(2)}</Tag>;
        return <Tag color="green">{risk.toFixed(2)}</Tag>;
      },
    },
  ];

  const statCards = [
    { title: "Total Notices", value: stats?.total || 0 },
    { title: "High Risk", value: stats?.high || 0, color: "red" },
    { title: "Medium Risk", value: stats?.medium || 0, color: "orange" },
    { title: "Low Risk", value: stats?.low || 0, color: "green" },
    { title: "Overdue + High", value: stats?.overdue_high || 0, color: "crimson" },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {statCards.map((item, index) => (
          <Col span={4} key={index}>
            <Card size="small" hoverable>
              <div
                style={{
                  fontSize: 20,
                  fontWeight: 600,
                  color: item.color || "#000",
                }}
              >
                {item.value}
              </div>
              <div style={{ fontSize: 13, color: "#666" }}>
                {item.title}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Card size="small" title="Top Risky Notices">
        <Table
          columns={columns}
          dataSource={topNotices}
          pagination={false}
          size="small"
          loading={loading}
        />
      </Card>
    </div>
  );
};

export default Dashboard;