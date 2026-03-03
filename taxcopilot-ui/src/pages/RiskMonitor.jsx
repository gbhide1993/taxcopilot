import { Card, Row, Col, Statistic, Table, Tag } from "antd";
import { useEffect, useState } from "react";
import api from "../api/axios";

const RiskMonitor = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      const res = await api.get("/risk/monitor");
      setData(res.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: "Notice Number",
      dataIndex: "notice_number",
    },
    {
      title: "Due Date",
      dataIndex: "due_date",
    },
    {
      title: "Risk Score",
      dataIndex: "risk_score",
      render: (score) => {
        if (score >= 4) return <Tag color="red">{score.toFixed(2)}</Tag>;
        if (score >= 2.5) return <Tag color="orange">{score.toFixed(2)}</Tag>;
        return <Tag color="green">{score.toFixed(2)}</Tag>;
      },
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card>
            <Statistic title="Total Notices" value={data?.total || 0} />
          </Card>
        </Col>

        <Col span={4}>
          <Card>
            <Statistic
              title="High Risk"
              value={data?.high || 0}
              styles={{
                content: { color: "red" }
                }}
            />
          </Card>
        </Col>

        <Col span={4}>
          <Card>
            <Statistic
              title="Medium Risk"
              value={data?.medium || 0}
              styles={{
                content: { color: "orange" }
              }}
            />
          </Card>
        </Col>

        <Col span={4}>
          <Card>
            <Statistic
              title="Low Risk"
              value={data?.low || 0}
              styles={{
                content: { color: "green" }
              }}
            />
          </Card>
        </Col>

        <Col span={4}>
          <Card>
            <Statistic
              title="Overdue + High"
              value={data?.overdue_high || 0}
              styles={{
                content: { color: "crimson" }
              }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Top Risky Notices">
        <Table
          rowKey="notice_id"
          loading={loading}
          columns={columns}
          dataSource={data?.top_notices || []}
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default RiskMonitor;