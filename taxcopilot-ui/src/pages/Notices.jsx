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
  Dropdown,
  message,
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
  const [clients, setClients] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  const [filters, setFilters] = useState({
    status: null,
    section: "",
    client_id: null,
    from_date: null,
    to_date: null,
  });

  useEffect(() => {
    fetchData(page, pageSize, filters);
  }, [page, pageSize]);

  const fetchData = async (pageParam, pageSizeParam, activeFilters) => {
    try {
      setLoading(true);

      const [clientsRes, usersRes, noticesRes] = await Promise.all([
        api.get("/clients"),
        api.get("/users"),
        api.get("/notices", {
          params: {
            page: pageParam,
            page_size: pageSizeParam,
            status: activeFilters.status || undefined,
            section: activeFilters.section || undefined,
            client_id: activeFilters.client_id || undefined,
            from_date: activeFilters.from_date || undefined,
            to_date: activeFilters.to_date || undefined,
          },
        }),
      ]);

      setClients(clientsRes.data || []);
      setUsers(usersRes.data || []);

      const clientMapping = {};
      (clientsRes.data || []).forEach((client) => {
        clientMapping[client.id] = client.name;
      });

      const userMapping = {};
      (usersRes.data || []).forEach((user) => {
        userMapping[user.id] = user.full_name;
      });

      const items = noticesRes.data?.items || [];
      const totalCount = noticesRes.data?.total || 0;

      const formatted = items.map((item) => ({
        key: item.id,
        notice: item.notice_number,
        client: clientMapping[item.client_id] || "—",
        section: item.section_reference || "—",
        dueDate: item.due_date
          ? dayjs(item.due_date).format("DD MMM YYYY")
          : "—",
        risk: item.risk_score ?? 0,
        status: item.status,
        assigned: item.assigned_to
          ? userMapping[item.assigned_to] || "Unknown"
          : "Unassigned",
        raw: item,
      }));

      setData(formatted);
      setTotal(totalCount);
    } catch (error) {
      console.error(error);
      message.error("Failed to load notices");
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (noticeId, newStatus) => {
    try {
      await api.patch(`/notices/${noticeId}/status`, { status: newStatus });

      message.success(`Status updated to ${newStatus}`);

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
    } catch {
      message.error("Failed to update status");
    }
  };

  const handleAssign = async (noticeId, userId) => {
    try {
      await api.put(`/notices/${noticeId}/assign`, {
        assigned_to: userId,
      });

      message.success("Notice assigned successfully");

      setData((prev) =>
        prev.map((item) =>
          item.raw.id === noticeId
            ? {
                ...item,
                assigned:
                  users.find((u) => u.id === userId)?.full_name ||
                  "Assigned",
                raw: { ...item.raw, assigned_to: userId },
              }
            : item
        )
      );
    } catch {
      message.error("Assignment failed");
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

        const statusItems = statusOptions
          .filter((option) => option.key !== record.status)
          .map((option) => ({
            key: `status_${option.key}`,
            label: `Mark as ${option.label}`,
          }));

        const menuItems = [
          ...statusItems,
          { type: "divider" },
          ...users.map((user) => ({
            key: `assign_${user.id}`,
            label: `Assign to ${user.full_name}`,
          })),
        ];

        return (
          <Dropdown
            menu={{
              items: menuItems,
              onClick: ({ key }) => {
                if (key.startsWith("status_")) {
                  const newStatus = key.replace("status_", "");
                  handleStatusChange(record.raw.id, newStatus);
                }

                if (key.startsWith("assign_")) {
                  const userId = parseInt(key.replace("assign_", ""));
                  handleAssign(record.raw.id, userId);
                }
              },
            }}
          >
            <Button type="link">Actions</Button>
          </Dropdown>
        );
      },
    },
  ];

  return (
    <div>
      <Card size="small" style={{ marginBottom: 16 }}>
        <Form layout="vertical">
          <Row gutter={16}>
            <Col span={4}>
              <Form.Item label="Status">
                <Select
                  allowClear
                  value={filters.status}
                  onChange={(value) =>
                    setFilters((prev) => ({ ...prev, status: value }))
                  }
                >
                  <Select.Option value="open">Open</Select.Option>
                  <Select.Option value="in_progress">
                    In Progress
                  </Select.Option>
                  <Select.Option value="replied">Replied</Select.Option>
                  <Select.Option value="closed">Closed</Select.Option>
                </Select>
              </Form.Item>
            </Col>

            <Col span={4}>
              <Form.Item label="Section">
                <Input
                  value={filters.section}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      section: e.target.value,
                    }))
                  }
                />
              </Form.Item>
            </Col>

            <Col span={4}>
              <Form.Item label="Client">
                <Select
                  allowClear
                  value={filters.client_id}
                  onChange={(value) =>
                    setFilters((prev) => ({
                      ...prev,
                      client_id: value,
                    }))
                  }
                >
                  {clients.map((client) => (
                    <Select.Option key={client.id} value={client.id}>
                      {client.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col span={6}>
              <Form.Item label="Date Range">
                <RangePicker
                  style={{ width: "100%" }}
                  onChange={(dates) =>
                    setFilters((prev) => ({
                      ...prev,
                      from_date: dates
                        ? dates[0].format("YYYY-MM-DD")
                        : null,
                      to_date: dates
                        ? dates[1].format("YYYY-MM-DD")
                        : null,
                    }))
                  }
                />
              </Form.Item>
            </Col>

            <Col span={4} style={{ display: "flex", alignItems: "end" }}>
              <Button
                type="primary"
                style={{ marginRight: 8 }}
                onClick={() => {
                  setPage(1);
                  fetchData(1, pageSize, filters);
                }}
              >
                Filter
              </Button>

              <Button
                onClick={() => {
                  const resetFilters = {
                    status: null,
                    section: "",
                    client_id: null,
                    from_date: null,
                    to_date: null,
                  };
                  setFilters(resetFilters);
                  setPage(1);
                  fetchData(1, pageSize, resetFilters);
                }}
              >
                Clear
              </Button>
            </Col>
          </Row>
        </Form>
      </Card>

      <Card size="small">
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          size="small"
          pagination={{
            current: page,
            pageSize,
            total,
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