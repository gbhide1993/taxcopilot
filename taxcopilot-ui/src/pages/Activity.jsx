import { useEffect, useState } from "react";
import { Card, Table } from "antd";
import api from "../api/axios";
import dayjs from "dayjs";

const Activity = () => {

  const [data,setData] = useState([]);
  const [loading,setLoading] = useState(false);

  const fetchActivity = async()=>{

    try{

      setLoading(true);

      const res = await api.get("/activity");

      setData(res.data || []);

    }catch{

      console.error("Failed loading activity logs");

    }finally{

      setLoading(false);

    }

  };

  useEffect(()=>{
    fetchActivity();
  },[]);

 const columns = [

  {
    title: "Time",
    dataIndex: "timestamp",
    render: t => dayjs(t).format("DD MMM YYYY HH:mm"),
    width: 200
  },

  {
    title: "User",
    dataIndex: "user_id",
    width: 120
  },

  {
    title: "Event",
    dataIndex: "action",
    width: 200
  },

  {
    title: "Description",
    render: (_,record)=>{

      if(record.entity_type === "Client")
        return `Client: ${record.details?.client_name || ""}`

      return JSON.stringify(record.details)

    }
  }

];

  return(
   <div className="page-container">
    <Card title="Firm Activity Log" className="app-card">

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{pageSize:20}}
      />
   
    </Card>
    </div>

  );

};

export default Activity;