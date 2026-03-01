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
  message,
} from "antd";
import { useState, useEffect } from "react";
import api from "../api/axios";
import dayjs from "dayjs";
import { getStatusTag } from "../utils/statusUtils";
import { Dropdown } from "antd";

const { RangePicker } = DatePicker;

const Notices = () => {
  const [open, setOpen] = useState(false);
  const [selectedNotice, setSelectedNotice] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchData(page, pageSize);
  }, [page, pageSize]);

  const fetchData = async (pageParam, pageSizeParam) => {
    try {
      setLoading(true);

      const [clientsRes, noticesRes] = await Promise.all([
        api.get("/clients"),
        api.get("/notices", {
          params: {
            page: pageParam,
            page_size: pageSizeParam,
          },
        }),
      ]);

      const clientMapping = {};
      clientsRes.data.forEach((client) => {
        clientMapping[client.id] = client.name;
      });

      const formatted = noticesRes.data.items.map((item) => ({
        key: item.id,
        notice: item.notice_number,
        client: clientMapping[item.client_id] || "—",
        section: item.section_reference || "—",
        dueDate: dayjs(item.due_date).format("DD MMM YYYY"),
        risk: 0,
        status: item.status,
        assigned: item.assigned_to || "Unassigned",
        raw: item,
      }));

      setData(formatted);
      setTotal(noticesRes.data.total);

    } catch (error) {
      console.error("Error fetching notices:", error);
      message.error("Failed to load notices");
    } finally {
      setLoading(false);
    }
  };

const handleStatusChange = async (noticeId, newStatus) => {
  try {
    await api.patch(`/notices/${noticeId}/status`, {
      status: newStatus,
    });

    message.success(`Status updated to ${newStatus}`);

    // Optimistic UI update
    setData((prev) =>
      prev.map((item) =>
        item.raw.id === noticeId
          ? {
              ...item,
              status: newStatus,
              raw: { ...item.raw, status: newStatus },
            }
          : item
      )
    );

  } catch (error) {
    message.error("Failed to update status");
  }
};

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
    

    {
    title: "Actions",
    render: (_, record) => {
        const statusOptions = [
        { key: "open", label: "Open" },
        { key: "in_progress", label: "In Progress" },
        { key: "replied", label: "Replied" },
        { key: "closed", label: "Closed" },
        ];

        const menuItems = statusOptions
        .filter(option => option.key !== record.status)
        .map(option => ({
            key: option.key,
            label: option.label,
        }));

        return (
        <Dropdown
            menu={{
            items: menuItems,
            onClick: ({ key }) => {
                handleStatusChange(record.raw.id, key);
            },
            }}
        >
            <Button type="link">
            Change Status
            </Button>
        </Dropdown>
        );
    },
    }
  ];

  return (
    <div>
      {/* Filter Section (UI only for now) */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Form layout="vertical">
          <Row gutter={16}>
            <Col span={4}>
              <Form.Item label="Status">
                <Select placeholder="Select status" allowClear>
                  <Select.Option value="open">Open</Select.Option>
                  <Select.Option value="in_progress">In Progress</Select.Option>
                  <Select.Option value="replied">Replied</Select.Option>
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
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            pageSizeOptions: ["5", "10", "20", "50"],
            onChange: (newPage, newPageSize) => {
              setPage(newPage);
              setPageSize(newPageSize);
            },
          }}
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
        size="large"
        onClose={() => setOpen(false)}
        open={open}
      >
        {selectedNotice && (
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
        )}
      </Drawer>
    </div>
  );
};

export default Notices;