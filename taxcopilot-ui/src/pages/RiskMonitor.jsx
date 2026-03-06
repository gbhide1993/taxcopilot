import {
  Card,
  Table,
  Tag,
  Row,
  Col,
  Select,
  Drawer,
  Descriptions,
  message
} from "antd";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip
} from "recharts";

import { useState, useEffect } from "react";
import api from "../api/axios";

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

const RiskMonitor = () => {

  const [data, setData] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedNotice, setSelectedNotice] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [drawerLoading, setDrawerLoading] = useState(false);

  const [filters, setFilters] = useState({
    risk_level: "high",
    unassigned_only: false,
    overdue_only: false,
  });

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await api.get("/users");
        setUsers(res.data || []);
      } catch {
        message.error("Failed to load users");
      }
    };

    fetchUsers();
  }, []);

  const fetchRiskData = async () => {

    try {

      setLoading(true);

      const res = await api.get("/notices", {
        params: {
          risk_level: filters.risk_level,
          unassigned_only: filters.unassigned_only,
          overdue_only: filters.overdue_only,
          page: 1,
          page_size: 50,
        },
      });

      setData(res.data.items || []);

    } catch {
      message.error("Failed to load notices");
    } finally {
      setLoading(false);
    }

  };

  useEffect(() => {
    fetchRiskData();
  }, [filters]);

  // -----------------------
  // Workload by CA
  // -----------------------

  const assigneeMap = {};

  data.forEach(n => {
    const name = n.assigned_user_name || "Unassigned";
    assigneeMap[name] = (assigneeMap[name] || 0) + 1;
  });

  const workloadData = Object.keys(assigneeMap).map(name => ({
    name,
    notices: assigneeMap[name]
  }));

  // -----------------------
  // Section Risk Map
  // -----------------------

  const sectionMap = {};

  data.forEach(n => {

    const sec = n.section_reference || "Unknown";

    sectionMap[sec] = (sectionMap[sec] || 0) + 1;

  });

  const sectionRiskData = Object.keys(sectionMap).map(sec => ({
    section: sec,
    count: sectionMap[sec]
  }));

// -----------------------
// Client Litigation Exposure
// -----------------------

    const clientMap = {};

    data.forEach(n => {

    const client = n.client_name || `Client ${n.client_id}`;

    clientMap[client] = (clientMap[client] || 0) + 1;

    });

    const clientRiskData = Object.keys(clientMap).map(name => ({
    name,
    notices: clientMap[name]
    }));

  // -----------------------
  // Assign Notice
  // -----------------------

  const handleAssign = async (noticeId, userId) => {

    try {

      await api.put(`/notices/${noticeId}/assign`, {
        assigned_to: userId,
      });

      const user = users.find(u => u.id === userId);

      setData(prev =>
        prev.map(n =>
          n.id === noticeId
            ? {
                ...n,
                assigned_to: userId,
                assigned_user_name: user?.full_name
              }
            : n
        )
      );

      message.success("Notice reassigned");

    } catch {
      message.error("Assignment failed");
    }

  };

  // -----------------------
  // Drawer
  // -----------------------

  const openNoticeDrawer = async (notice) => {

    try {

      setDrawerLoading(true);
      setSelectedNotice(notice);
      setDrawerOpen(true);

      const timelineRes =
        await api.get(`/notices/${notice.id}/timeline`);

      setTimeline(timelineRes.data || []);

    } catch {

      message.error("Failed to load notice details");

    } finally {

      setDrawerLoading(false);

    }

  };

  // -----------------------
  // Risk Explanation
  // -----------------------

  const getRiskExplanation = (notice) => {

    const reasons = [];

    const today = new Date();
    const due = new Date(notice.due_date);

    const diff =
      Math.ceil((due - today)/(1000*60*60*24));

    if (notice.section_reference?.includes("143"))
      reasons.push("Scrutiny notice");

    if (notice.section_reference?.includes("148"))
      reasons.push("Reassessment risk");

    if (notice.section_reference?.includes("271"))
      reasons.push("Penalty exposure");

    if (diff <= 3 && diff >= 0)
      reasons.push(`Response deadline in ${diff} days`);

    if (diff < 0)
      reasons.push("Notice response already overdue");

    if (!notice.assigned_to)
      reasons.push("Notice currently unassigned");

    return reasons;

  };

  // -----------------------
  // Recommended Action
  // -----------------------

  const getRecommendedAction = (notice) => {

    const today = new Date();
    const due = new Date(notice.due_date);

    const diff =
      Math.ceil((due - today)/(1000*60*60*24));

    if (notice.risk_score >= 4 && !notice.assigned_to)
      return "Assign Senior CA immediately";

    if (notice.risk_score >= 3 && diff <= 3)
      return "Prepare response draft urgently";

    if (notice.risk_score >= 3)
      return "Assign CA and review notice";

    if (diff <= 7)
      return "Monitor timeline";

    return "Low priority";

  };

  // -----------------------
  // Escalation
  // -----------------------

  const getEscalationStatus = (record) => {

    const today = new Date();
    const due = new Date(record.due_date);

    const diff =
      Math.ceil((due - today)/(1000*60*60*24));

    if (diff < 0 && record.risk_score >= 3)
      return { label: "Severe", color: "red" };

    if (record.risk_score >= 4 && !record.assigned_to)
      return { label: "Critical", color: "volcano" };

    if (record.risk_score >= 3 && diff <= 3)
      return { label: "Attention", color: "orange" };

    return null;

  };

  // -----------------------
  // KPIs
  // -----------------------

  const critical =
    data.filter(n => n.risk_score >= 4).length;

  const high =
    data.filter(n => n.risk_score >= 3 && n.risk_score < 4).length;

  const unassigned =
    data.filter(n => !n.assigned_to).length;

  const dueSoon =
    data.filter(n => {

      const diff =
        Math.ceil((new Date(n.due_date)-new Date())/(1000*60*60*24));

      return diff <=7 && diff >=0;

    }).length;

  // -----------------------
  // Table Columns
  // -----------------------

  const columns = [

    {
      title: "Notice",
      dataIndex: "notice_number",
      width: 250
    },

    {
      title: "Section",
      dataIndex: "section_reference",
      width: 150
    },

    {
      title: "Risk",
      dataIndex: "risk_score",
      width: 120,
      render: r => {

        if (r >= 4) return <Tag color="red">Critical {r}</Tag>;
        if (r >= 3) return <Tag color="volcano">High {r}</Tag>;
        if (r >= 2) return <Tag color="orange">Medium {r}</Tag>;

        return <Tag color="green">Low {r}</Tag>;

      }
    },

    {
      title: "Escalation",
      width: 150,
      render: (_, record) => {

        const esc = getEscalationStatus(record);

        if (!esc) return "—";

        return <Tag color={esc.color}>🔥 {esc.label}</Tag>;

      }
    },

    {
      title: "Recommended Action",
      width: 250,
      render: (_, record) => (
        <Tag color="blue">
          {getRecommendedAction(record)}
        </Tag>
      )
    },

    {
      title: "Assigned To",
      width: 220,
      render: (_, record) => (

        <div onClick={e => e.stopPropagation()}>

          <Select
            size="small"
            value={record.assigned_to || undefined}
            placeholder="Assign"
            style={{ width: "100%" }}
            onChange={(val) => handleAssign(record.id, val)}
          >

            {users.map(user => (
              <Select.Option key={user.id} value={user.id}>
                {user.full_name}
              </Select.Option>
            ))}

          </Select>

        </div>

      )
    }

  ];

  return (

    <div>

      {/* KPI CARDS */}

      <Row gutter={16} style={{ marginBottom: 16 }}>

        <Col span={6}>
          <Card size="small">
            🔴 Critical Risk
            <h2>{critical}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            🟠 High Risk
            <h2>{high}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            ⚠ Due This Week
            <h2>{dueSoon}</h2>
          </Card>
        </Col>

        <Col span={6}>
          <Card size="small">
            👤 Unassigned
            <h2>{unassigned}</h2>
          </Card>
        </Col>

      </Row>

      {/* ANALYTICS */}

      <Row gutter={16} style={{ marginBottom: 16 }}>

        <Col span={12}>
          <Card title="Notice Workload by CA" size="small" style={{ height: 240 }}>

            <BarChart
                layout="vertical"
                width={350}
                height={180}
                data={workloadData}
               >
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip />
                <Bar dataKey="notices" fill="#1890ff" radius={[0,4,4,0]} />
            </BarChart>

          </Card>
        </Col>

        <Col span={12}>
          <Card title="Section Risk Distribution" size="small">

            <BarChart
                layout="vertical"
                width={350}
                height={180}
                data={sectionRiskData}
               >
                <XAxis type="number" />
                <YAxis dataKey="section" type="category" />
                <Tooltip />
                <Bar dataKey="count" fill="#ff7875" radius={[0,4,4,0]} />
            </BarChart>

          </Card>
        </Col>

      </Row>

        <Row gutter={16} style={{ marginBottom: 16 }}>

        <Col span={24}>
            <Card title="Client Litigation Exposure" size="small">

            <BarChart
                layout="vertical"
                width={350}
                height={180}
                data={clientRiskData}
            >
                <XAxis type="number"/>
                <YAxis dataKey="name" type="category"/>
                <Tooltip/>
                <Bar
                dataKey="notices"
                fill="#722ed1"
                radius={[0,4,4,0]}
                />
            </BarChart>

            </Card>
        </Col>

        </Row>

      {/* TABLE */}

      <Card size="small">

        <Table
          rowKey="id"
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={false}
          scroll={{ x: 1200 }}
          onRow={(record) => ({
            onClick: () => openNoticeDrawer(record)
          })}
          rowClassName={(record) => {
            if (record.risk_severity === "CRITICAL") return "row-critical";
            if (record.risk_severity === "HIGH") return "row-high-risk";
            if (record.risk_severity === "MEDIUM") return "row-medium-risk";
            return "";
          }}
        />

      </Card>

      {/* DRAWER */}

      <Drawer
        title="Notice Details"
        placement="right"
        size="large"
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
      >

        {drawerLoading ? (
          <div>Loading...</div>
        ) : selectedNotice && (

          <>

            <Descriptions bordered column={1} size="small">

              <Descriptions.Item label="Notice Number">
                {selectedNotice.notice_number}
              </Descriptions.Item>

              <Descriptions.Item label="Section">
                {selectedNotice.section_reference}
              </Descriptions.Item>

              <Descriptions.Item label="Risk Score">
                {selectedNotice.risk_score}
              </Descriptions.Item>

              <Descriptions.Item label="Status">
                {selectedNotice.status}
              </Descriptions.Item>

            </Descriptions>

            <div style={{ marginTop: 24 }}>

              <h4>Risk Analysis</h4>

              <ul>
                {getRiskExplanation(selectedNotice).map((r,i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>

            </div>

            <div style={{ marginTop: 24 }}>

              <h4>Activity Timeline</h4>

              <ul>

                {timeline.map((entry,index) => (

                  <li key={index}>

                    <strong>{entry.event_type}</strong>

                    — {entry.description}

                    <br/>

                    <small>

                      {dayjs
                        .utc(entry.created_at)
                        .local()
                        .format("DD MMM YYYY HH:mm")}

                    </small>

                  </li>

                ))}

              </ul>

            </div>

          </>

        )}

      </Drawer>

    </div>

  );

};

export default RiskMonitor;