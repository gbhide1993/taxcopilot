import { Card, Row, Col, Table, Tag } from "antd";
import { useEffect, useState } from "react";
import api from "../api/axios";
import dayjs from "dayjs";

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [workQueue, setWorkQueue] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      const [monitorRes, queueRes] = await Promise.all([
        api.get("/risk/monitor"),
        api.get("/risk/work-queue"),
      ]);

      setStats(monitorRes.data);

      setWorkQueue(
        queueRes.data.map((item) => ({
          key: item.notice_id,
          notice: item.notice_number,
          dueDate: dayjs(item.due_date).format("DD MMM YYYY"),
          risk: item.risk_score,
          priority: item.priority,
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
    {
      title: "Priority",
      dataIndex: "priority",
      render: (priority) => {
        if (priority === 1) return <Tag color="red">Critical</Tag>;
        if (priority === 2) return <Tag color="volcano">High</Tag>;
        if (priority === 3) return <Tag color="orange">Due Soon</Tag>;
        return <Tag color="blue">Medium</Tag>;
      },
    },
  ];

  const statCards = stats
    ? [
        { title: "Total Notices", value: stats.total },
        { title: "High Risk", value: stats.high, color: "red" },
        { title: "Medium Risk", value: stats.medium, color: "orange" },
        { title: "Low Risk", value: stats.low, color: "green" },
        { title: "Overdue + High", value: stats.overdue_high, color: "crimson" },
      ]
    : [];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {statCards.map((item, index) => (
          <Col span={4} key={index}>
            <Card size="small">
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

      <Card size="small" title="Priority Work Queue">
        <Table
          columns={columns}
          dataSource={workQueue}
          pagination={false}
          size="small"
          loading={loading}
        />
      </Card>
    </div>
  );
};

export default Dashboard;