import {
  Card,
  Table,
  Tag,
  Form,
  Select,
  DatePicker,
  Input,
  Button,
  Row,
  Col,
  Drawer,
  Descriptions,
} from "antd";
import { useState, useEffect } from "react";
import api from "../api/axios";
import dayjs from "dayjs";
import { getStatusTag } from "../utils/statusUtils";


const { RangePicker } = DatePicker;

const Notices = () => {
  const [open, setOpen] = useState(false);
  const [selectedNotice, setSelectedNotice] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const columns = [
    { title: "Notice Number", dataIndex: "notice" },
    { title: "Client", dataIndex: "client" },
    { title: "Section", dataIndex: "section" },
    { title: "Due Date", dataIndex: "dueDate" },
    { title: "Risk Score", dataIndex: "risk" },
    
    {
    title: "Status",
    dataIndex: "status",
    render: (status) => {
        const { label, color } = getStatusTag(status);
        return <Tag color={color}>{label}</Tag>;
  },
},
    
    { title: "Assigned To", dataIndex: "assigned" },
  ];

  

  useEffect(() => {
  fetchNotices();
}, []);

const fetchNotices = async () => {
  try {
    setLoading(true);
    const response = await api.get("/notices");

    const formatted = response.data.map((item) => ({
      key: item.id,
      notice: item.notice_number,
      client: `Client #${item.client_id}`,
      section: item.section_reference,
      dueDate: dayjs(item.due_date).format("DD MMM YYYY"),
      risk: 0,
      status: item.status,
      assigned: `User #${item.assigned_to}`,
      raw: item,
    }));

    setData(formatted);
  } catch (error) {
    console.error("Error fetching notices:", error);
  } finally {
    setLoading(false);
  }
};

  return (
    <div>
      {/* Filter Section */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Form layout="vertical">
          <Row gutter={16}>
            <Col span={4}>
              <Form.Item label="Status">
                <Select placeholder="Select status" allowClear>
                  <Select.Option value="open">Open</Select.Option>
                  <Select.Option value="overdue">Overdue</Select.Option>
                  <Select.Option value="closed">Closed</Select.Option>
                </Select>
              </Form.Item>
            </Col>

            <Col span={4}>
              <Form.Item label="Section">
                <Input placeholder="Search section" />
              </Form.Item>
            </Col>

            <Col span={4}>
              <Form.Item label="Client">
                <Input placeholder="Search client" />
              </Form.Item>
            </Col>

            <Col span={6}>
              <Form.Item label="Date Range">
                <RangePicker style={{ width: "100%" }} />
              </Form.Item>
            </Col>

            <Col span={4} style={{ display: "flex", alignItems: "end" }}>
              <Button type="primary" style={{ marginRight: 8 }}>
                Filter
              </Button>
              <Button>Clear</Button>
            </Col>
          </Row>
        </Form>
      </Card>

      {/* Table Section */}
      <Card size="small">
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          size="small"
          onRow={(record) => ({
            onClick: () => {
              setSelectedNotice(record);
              setOpen(true);
            },
          })}
        />
      </Card>

      {/* Drawer Section */}
      <Drawer
        title="Notice Details"
        placement="right"
        width={720}
        onClose={() => setOpen(false)}
        open={open}
      >
        {selectedNotice && (
          <>
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="Notice Number">
                {selectedNotice.notice}
              </Descriptions.Item>
              <Descriptions.Item label="Client">
                {selectedNotice.client}
              </Descriptions.Item>
              <Descriptions.Item label="Section">
                {selectedNotice.section}
              </Descriptions.Item>
              <Descriptions.Item label="Due Date">
                {selectedNotice.dueDate}
              </Descriptions.Item>
              <Descriptions.Item label="Risk Score">
                {selectedNotice.risk}
              </Descriptions.Item>
              <Descriptions.Item label="Assigned To">
                {selectedNotice.assigned}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 24 }}>
              <h4>Draft Versions</h4>
              <p>Version 1 - Generated on 10 Mar 2026</p>
              <p>Version 2 - Generated on 15 Mar 2026</p>
            </div>

            <div style={{ marginTop: 24 }}>
              <h4>Appeal Versions</h4>
              <p>No appeals generated yet.</p>
            </div>

            <div style={{ marginTop: 24 }}>
              <h4>Risk Metadata</h4>
              <p>Late filing history detected.</p>
              <p>High variance in declared income.</p>
            </div>
          </>
        )}
      </Drawer>
    </div>
  );
};

export default Notices;