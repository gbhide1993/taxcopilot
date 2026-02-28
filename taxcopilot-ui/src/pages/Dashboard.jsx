import { Card, Row, Col, Table, Tag } from "antd";

const Dashboard = () => {
  const stats = [
    { title: "Total Active Notices", value: 24 },
    { title: "Overdue Notices", value: 5 },
    { title: "High Risk Notices", value: 7 },
    { title: "Draft Pending", value: 4 },
    { title: "Appeals Pending", value: 2 },
    { title: "Closed This Month", value: 12 },
  ];

  const columns = [
    { title: "Notice Number", dataIndex: "notice" },
    { title: "Client", dataIndex: "client" },
    { title: "Section", dataIndex: "section" },
    { title: "Due Date", dataIndex: "dueDate" },
    { title: "Days Remaining", dataIndex: "daysRemaining" },
    { title: "Risk Score", dataIndex: "risk" },
    {
      title: "Status",
      dataIndex: "status",
      render: (status) => {
        if (status === "Overdue") return <Tag color="red">Overdue</Tag>;
        if (status === "High Risk") return <Tag color="orange">High Risk</Tag>;
        return <Tag color="green">{status}</Tag>;
      },
    },
    { title: "Assigned To", dataIndex: "assigned" },
    {
  title: "Actions",
  render: () => (
    <>
      <a style={{ marginRight: 12 }}>Draft</a>
      <a style={{ marginRight: 12 }}>Appeal</a>
      <a>Close</a>
    </>
  ),
},
  ];

  const data = [
    {
      key: 1,
      notice: "N-101",
      client: "ABC Pvt Ltd",
      section: "143(2)",
      dueDate: "25 Mar 2026",
      daysRemaining: -3,
      risk: 82,
      status: "Overdue",
      assigned: "Rahul",
    },
    {
      key: 2,
      notice: "N-102",
      client: "XYZ Traders",
      section: "148",
      dueDate: "02 Apr 2026",
      daysRemaining: 5,
      risk: 75,
      status: "High Risk",
      assigned: "Priya",
    },
    {
      key: 3,
      notice: "N-103",
      client: "MNO LLP",
      section: "133(6)",
      dueDate: "10 Apr 2026",
      daysRemaining: 12,
      risk: 40,
      status: "Open",
      assigned: "Amit",
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
  {stats.map((item, index) => (
    <Col span={4} key={index}>
      <Card
        size="small"
        hoverable
        onClick={() => console.log(item.title)}
        style={{ cursor: "pointer" }}
      >
        <div style={{ fontSize: 20, fontWeight: 600 }}>
          {item.value}
        </div>
        <div style={{ fontSize: 13, color: "#666" }}>
          {item.title}
        </div>
      </Card>
    </Col>
  ))}
</Row>

      <Card size="small" title="Work Queue">
        <Table
          columns={columns}
          dataSource={data}
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
};

export default Dashboard;