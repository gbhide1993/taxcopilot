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
  const [noticeDetail, setNoticeDetail] = useState(null);
  const [draftVersions, setDraftVersions] = useState([]);
  const [appealVersions, setAppealVersions] = useState([]);
  const [riskData, setRiskData] = useState(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
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

const fetchNoticeDetail = async (noticeId) => {
  try {
    setDrawerLoading(true);
    setRiskData(null);
    setNoticeDetail(null);
    setDraftVersions([]);
    setAppealVersions([]);

    const detailRes = await api.get(`/notices/${noticeId}`);

    const draftRes = await api
      .get(`/draft/${noticeId}/versions`)
      .catch(() => ({ data: [] }));

    const appealRes = await api
      .get(`/appeals/${noticeId}/versions`)
      .catch(() => ({ data: [] }));

    const draftData = draftRes.data;
    const appealData = appealRes.data;

    setNoticeDetail(detailRes.data || {});

    setDraftVersions(
      Array.isArray(draftData)
        ? draftData
        : draftData?.versions || []
    );

    setAppealVersions(
      Array.isArray(appealData)
        ? appealData
        : appealData?.versions || []
    );

  } catch (error) {
    console.error(error);
    message.error("Failed to load notice details");
  } finally {
    setDrawerLoading(false);
  }
};


const handleRiskCalculation = async (noticeId) => {
  try {
    const res = await api.post(`/risk/calculate/${noticeId}`);

    const score = res.data?.score ?? null;

    setRiskData(res.data);

    // 🔥 Update table row dynamically
    setData((prev) =>
      prev.map((item) =>
        item.raw.id === noticeId
          ? {
              ...item,
              risk: score,
              raw: { ...item.raw, risk_score: score },
            }
          : item
      )
    );

    message.success("Risk calculated");
  } catch (error) {
    console.error(error);
    message.error("Risk calculation failed");
  }
};

const handleGenerateDraft = async (noticeId) => {
  try {
    await api.post(`/draft/generate/${noticeId}`);
    message.success("Draft generated");
    fetchNoticeDetail(noticeId);
  } catch {
    message.error("Draft generation failed");
  }
};

const handleExportDraft = async (noticeId, versionNumber) => {
  try {
    const response = await api.get(
      `/draft/${noticeId}/export/${versionNumber}`,
      {
        responseType: "blob",
      }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `draft_notice_${noticeId}_v${versionNumber}.docx`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();

    message.success("Draft downloaded");
  } catch (error) {
    message.error("Failed to export draft");
  }
};

const handleGenerateAppeal = async (noticeId) => {
  try {
    await api.post(`/appeals/generate/${noticeId}`);
    message.success("Appeal generated");
    fetchNoticeDetail(noticeId);
  } catch {
    message.error("Appeal generation failed");
  }
};

const handleExportAppeal = async (noticeId, versionNumber) => {
  try {
    const response = await api.get(
      `/appeals/${noticeId}/export/${versionNumber}`,
      {
        responseType: "blob",
      }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `appeal_notice_${noticeId}_v${versionNumber}.docx`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();

    message.success("Appeal downloaded");
  } catch (error) {
    message.error("Failed to export appeal");
  }
};

  const columns = [
    { title: "Notice Number", dataIndex: "notice" },
    { title: "Client", dataIndex: "client" },
    { title: "Section", dataIndex: "section" },
    { title: "Due Date", dataIndex: "dueDate" },
    {
    title: "Risk Score",
    dataIndex: "risk",
    sorter: (a, b) => (a.risk || 0) - (b.risk || 0),
    sortDirections: ["descend", "ascend"],
    defaultSortOrder: "descend",
    render: (risk) => {
        if (risk == null) return "—";

        let color = "green";
        if (risk >= 4) color = "red";
        else if (risk >= 2.5) color = "orange";

        return <Tag color={color}>{risk}</Tag>;
    },
    },
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
              fetchNoticeDetail(record.raw.id);
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
  {drawerLoading ? (
    <div style={{ padding: 24 }}>Loading...</div>
  ) : !noticeDetail ? (
    <div style={{ padding: 24 }}>No data available</div>
  ) : (
    <>
      <Descriptions bordered column={1} size="small">
        <Descriptions.Item label="Notice Number">
          {noticeDetail.notice_number || "—"}
        </Descriptions.Item>
        <Descriptions.Item label="Section">
          {noticeDetail.section_reference || "—"}
        </Descriptions.Item>
        <Descriptions.Item label="Assessment Year">
          {noticeDetail.assessment_year || "—"}
        </Descriptions.Item>
        <Descriptions.Item label="Status">
          {noticeDetail.status || "—"}
        </Descriptions.Item>
      </Descriptions>

      <div style={{ marginTop: 24 }}>
        <h4>Risk</h4>
        <Button
          type="primary"
          onClick={() => handleRiskCalculation(noticeDetail.id)}
        >
          Calculate Risk
        </Button>

        {riskData && (
          <div style={{ marginTop: 12 }}>
            <p>Risk Score: {riskData?.score ?? "—"}</p>
          </div>
        )}
      </div>

        <div style={{ marginTop: 24 }}>
  <h4>Drafts</h4>

  <Button
    type="primary"
    style={{ marginBottom: 12 }}
    onClick={() => handleGenerateDraft(noticeDetail.id)}
  >
    Generate Draft
  </Button>

  <Table
    size="small"
    rowKey="version_number"
    dataSource={draftVersions}
    pagination={false}
    columns={[
      {
        title: "Version",
        dataIndex: "version_number",
        render: (v) => `V${v}`,
      },
      {
        title: "Actions",
        render: (_, record) => (
          <Button
            type="link"
            onClick={() =>
              handleExportDraft(noticeDetail.id, record.version_number)
            }
          >
            Export DOCX
          </Button>
        ),
      },
    ]}
  />
</div>
     

      <div style={{ marginTop: 24 }}>
  <h4>Appeals</h4>

  <Button
    type="primary"
    style={{ marginBottom: 12 }}
    onClick={() => handleGenerateAppeal(noticeDetail.id)}
  >
    Generate Appeal
  </Button>

  <Table
    size="small"
    rowKey="version_number"
    dataSource={appealVersions}
    pagination={false}
    columns={[
      {
        title: "Version",
        dataIndex: "version_number",
        render: (v) => `V${v}`,
      },
      {
        title: "Actions",
        render: (_, record) => (
          <Button
            type="link"
            onClick={() =>
              handleExportAppeal(noticeDetail.id, record.version_number)
            }
          >
            Export DOCX
          </Button>
        ),
      },
    ]}
  />
</div>


    </>
  )}
</Drawer>


    </div>
  );
};

export default Notices;