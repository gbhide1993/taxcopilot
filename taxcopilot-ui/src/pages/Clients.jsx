import {
  Card,
  Table,
  Tag,
  Button,
  Modal,
  Form,
  Input,
  Select,
  message,
  Drawer,
  List,
  Divider
} from "antd";

import { useState, useEffect } from "react";
import api from "../api/axios";

const Clients = () => {

  const [data,setData] = useState([]);
  const [users,setUsers] = useState([]);
  const [loading,setLoading] = useState(false);

  const [drawerOpen,setDrawerOpen] = useState(false);
  const [selectedClient,setSelectedClient] = useState(null);
  const [clientHistory,setClientHistory] = useState(null);

  const [modalOpen,setModalOpen] = useState(false);
  const [editingClient,setEditingClient] = useState(null);

  const [form] = Form.useForm();

  const fetchClients = async () => {

    try{

      setLoading(true);

      const [clientsRes,usersRes] = await Promise.all([
        api.get("/clients"),
        api.get("/users")
      ]);

      setData(clientsRes.data || []);
      setUsers(usersRes.data || []);

    }catch{

      message.error("Failed to load clients");

    }finally{

      setLoading(false);

    }

  };

  useEffect(()=>{
    fetchClients();
  },[]);


  /* ---------------- Drawer Logic ---------------- */

  const openClientDrawer = async(client)=>{

    try{

      setSelectedClient(client);
      setDrawerOpen(true);

      const res = await api.get(`/clients/${client.id}/compliance-summary`);

      setClientHistory(res.data);

    }catch{

      message.error("Failed to load client history");

    }

  };


  /* ---------------- Modal Logic ---------------- */

  const openCreateModal = ()=>{

    setEditingClient(null);
    form.resetFields();
    setModalOpen(true);

  };

  const openEditModal = (record)=>{

    setEditingClient(record);

    form.setFieldsValue({
      name: record.name,
      pan: record.pan,
      assigned_to: record.assigned_to
    });

    setModalOpen(true);

  };

  const handleSave = async ()=>{

    try{

      const values = await form.validateFields();

      if(editingClient){

        await api.put(`/clients/${editingClient.id}`,values);

        message.success("Client updated");

      }else{

        await api.post("/clients",values);

        message.success("Client created");

      }

      setModalOpen(false);
      fetchClients();

    }catch{

      message.error("Failed to save client");

    }

  };


  /* ---------------- Table Columns ---------------- */

  const columns = [

    {
      title:"Client Name",
      dataIndex:"name",
      render:(v,record)=>(
        <a onClick={()=>openClientDrawer(record)}>
          {v}
        </a>
      )
    },

    {
      title:"PAN",
      dataIndex:"pan"
    },

    {
      title:"Email",
      dataIndex:"email",
      render:(v)=>v || "—"
    },

    {
      title:"Mobile",
      dataIndex:"phone",
      render:(v)=>v || "—"
    },

    {
      title:"Assigned CA",
      render:(_,record)=>{

        const user = users.find(u=>u.id===record.assigned_to);

        return user?.full_name || "—";

      }
    },

    {
      title:"Active Notices",
      dataIndex:"notice_count"
    },

    {
      title:"Risk Exposure",
      render:(_,record)=>{

        const r = record.risk_score || 0;

        if(r>=4) return <Tag color="red">Critical</Tag>;
        if(r>=3) return <Tag color="volcano">High</Tag>;
        if(r>=2) return <Tag color="orange">Medium</Tag>;

        return <Tag color="green">Low</Tag>;

      }
    },

    {
      title:"Actions",
      render:(_,record)=>(
        <Button
          size="small"
          onClick={()=>openEditModal(record)}
        >
          Edit
        </Button>
      )
    }

  ];



  return(

    <div className="page-container">

      <Card className="app-card"
        size="small"
        title="Clients"
        extra={
          <Button
            type="primary"
            onClick={openCreateModal}
          >
            Add Client
          </Button>
        }
      >
        <div className="app-table">
        <Table
          rowKey="id"
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={{pageSize:10}}
        />
        </div>
      </Card>



      {/* ---------------- Drawer ---------------- */}

      <Drawer
        title={selectedClient?.name}
        open={drawerOpen}
        onClose={()=>setDrawerOpen(false)}
        width={500}
      >

        <Divider>Notices</Divider>

        <List
          dataSource={clientHistory?.notices || []}
          renderItem={(item)=>(
            <List.Item>
              Notice #{item.notice_number} – {item.section_reference}
            </List.Item>
          )}
        />

        <Divider>Drafts</Divider>

        <List
          dataSource={clientHistory?.drafts || []}
          renderItem={(item)=>(
            <List.Item>
              Draft Version {item.version_number}
            </List.Item>
          )}
        />

        <Divider>Appeals</Divider>

        <List
          dataSource={clientHistory?.appeals || []}
          renderItem={(item)=>(
            <List.Item>
              Appeal Version {item.version_number}
            </List.Item>
          )}
        />

      </Drawer>



      {/* ---------------- Modal ---------------- */}

      <Modal
        title={editingClient?"Edit Client":"Add Client"}
        open={modalOpen}
        onCancel={()=>setModalOpen(false)}
        onOk={handleSave}
      >

        <Form form={form} layout="vertical">

          <Form.Item
            label="Client Name"
            name="name"
            rules={[{required:true}]}
          >
            <Input/>
          </Form.Item>

          <Form.Item
            label="PAN"
            name="pan"
          >
            <Input/>
          </Form.Item>

          <Form.Item
            label="E-mail"
            name="email"
          >
            <Input/>
          </Form.Item>

          <Form.Item
            label="Mobile"
            name="phone"
          >
            <Input/>
          </Form.Item>

          <Form.Item
            label="Assigned CA"
            name="assigned_to"
          >

            <Select allowClear>

              {users.map(u=>(
                <Select.Option key={u.id} value={u.id}>
                  {u.full_name}
                </Select.Option>
              ))}

            </Select>

          </Form.Item>

        </Form>

      </Modal>

    </div>

  );

};

export default Clients;