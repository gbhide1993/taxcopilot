import { useEffect, useState } from "react";
import { Card, Table, Button } from "antd";
import api from "../api/axios";
import dayjs from "dayjs";

const Appeals = () => {

  const [data,setData] = useState([]);
  const [loading,setLoading] = useState(false);

  const fetchAppeals = async () => {

    try {

      setLoading(true);

      const res = await api.get("/appeals/");

      setData(res.data || []);

    } catch {

      console.error("Failed to load appeals");

    } finally {

      setLoading(false);

    }

  };

  useEffect(()=>{
    fetchAppeals();
  },[]);

  const columns = [

    {
      title:"Client",
      dataIndex:"client_name",
      width:220
    },

    {
      title:"Notice",
      dataIndex:"notice_number",
      width:260
    },

    {
      title:"Section",
      dataIndex:"section_reference",
      width:140
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
      render:v=>dayjs(v).format("DD MMM YYYY"),
      width:160
    },

    {
      title:"Actions",
      render:(_,record)=>(
        <Button
          type="primary"
          size="small"
          href={`http://localhost:8000/appeals/${record.notice_id}/export/${record.version_number}`}
        >
          Download
        </Button>
      )
    }

  ];

  return(

    <Card title="Appeal Repository">

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{pageSize:20}}
      />

    </Card>

  );

};

export default Appeals;