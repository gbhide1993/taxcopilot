import { useEffect, useState } from "react";
import { Card, Table, Button } from "antd";
import api from "../api/axios";
import dayjs from "dayjs";

const Drafts = () => {

  const [data,setData] = useState([]);
  const [loading,setLoading] = useState(false);

  const fetchDrafts = async () => {

    try {

      setLoading(true);

      const res = await api.get("/draft/");

      setData(res.data || []);

    } catch {
      console.error("Failed to load drafts");
    } finally {
      setLoading(false);
    }

  };

  useEffect(() => {
    fetchDrafts();
  }, []);

const columns = [

  {
    title:"Client",
    dataIndex:"client_name",
    width:200
  },
  
  {
    title:"Notice",
    dataIndex:"notice_number",
    width:250
  },

  {
    title:"Section",
    dataIndex:"section_reference",
    width:150
  },

  {
    title:"Version",
    dataIndex:"version_number",
    render:v=>`V${v}`,
    width:100
  },

  {
    title:"Created",
    dataIndex:"created_at",
    render:(v)=>dayjs(v).format("DD MMM YYYY"),
    width:200
  },

  {
    title:"Actions",
    render:(_,record)=>(
      <Button
        size="small"
        type="primary"
        href={`http://localhost:8000/draft/${record.notice_id}/export/${record.version_number}`}
      >
        Download DOCX
      </Button>
    )
  }

];

  return (

    <Card title="Draft Repository">

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{ pageSize:20 }}
      />

    </Card>

  );

};

export default Drafts;