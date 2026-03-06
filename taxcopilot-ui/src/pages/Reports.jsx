import { useEffect, useState } from "react";
import { Card, Row, Col, Table, Button, Space } from "antd";
import api from "../api/axios";

import {
  WarningOutlined,
  ClockCircleOutlined,
  TeamOutlined,
  BarChartOutlined,
  FileExcelOutlined
} from "@ant-design/icons";

const Reports = () => {

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {

    try {

      setLoading(true);

      const res = await api.get("/reports");

      setData(res.data);

    } catch (err) {

      console.error("Failed to load reports", err);

    } finally {

      setLoading(false);

    }

  };

  useEffect(() => {

    fetchReports();

  }, []);

  if (!data) return null;

  return (

    <div>

      {/* =========================
         KPI SUMMARY
      ========================== */}

      <Row gutter={16} style={{ marginBottom: 20 }}>

        <Col span={8}>
          <Card size="small">
            Total Notices
            <h2>{data.total_notices}</h2>
          </Card>
        </Col>

        <Col span={8}>
          <Card size="small">
            High Risk
            <h2>{data.high_risk}</h2>
          </Card>
        </Col>

        <Col span={8}>
          <Card size="small">
            Overdue
            <h2>{data.overdue}</h2>
          </Card>
        </Col>

      </Row>

      {/* =========================
         EXPORT REPORTS
      ========================== */}

      <Card
        title="Export Reports"
        style={{ marginBottom: 20 }}
      >

        <Space size="large" wrap>

          <Button
            type="primary"
            icon={<WarningOutlined />}
            href="http://localhost:8000/reports/export?type=high-risk"
          >
            High Risk Notices
          </Button>

          <Button
            danger
            icon={<ClockCircleOutlined />}
            href="http://localhost:8000/reports/export?type=overdue"
          >
            Overdue Notices
          </Button>

          <Button
            style={{ background: "#52c41a", color: "#fff" }}
            icon={<TeamOutlined />}
            href="http://localhost:8000/reports/export?type=client-summary"
          >
            Client Exposure
          </Button>

          <Button
            style={{ background: "#fa8c16", color: "#fff" }}
            icon={<BarChartOutlined />}
            href="http://localhost:8000/reports/export?type=section-summary"
          >
            Section Exposure
          </Button>

          <Button
            style={{ background: "#13c2c2", color: "#fff" }}
            icon={<FileExcelOutlined />}
            href="http://localhost:8000/reports/export?type=workload"
          >
            CA Workload
          </Button>

        </Space>

      </Card>

      {/* =========================
         CLIENT DISTRIBUTION
      ========================== */}

      <Card
        title="Notices by Client"
        style={{ marginBottom: 20 }}
      >

        <Table
          rowKey="client"
          dataSource={data.client_distribution}
          loading={loading}
          pagination={false}
          columns={[
            {
              title: "Client",
              dataIndex: "client"
            },
            {
              title: "Total Notices",
              dataIndex: "count"
            }
          ]}
        />

      </Card>

      {/* =========================
         SECTION DISTRIBUTION
      ========================== */}

      <Card title="Notices by Section">

        <Table
          rowKey="section"
          dataSource={data.section_distribution}
          loading={loading}
          pagination={false}
          columns={[
            {
              title: "Section",
              dataIndex: "section"
            },
            {
              title: "Notice Count",
              dataIndex: "count"
            }
          ]}
        />

      </Card>

    </div>

  );

};

export default Reports;