import { useEffect, useState } from "react";
import { Card, Switch, InputNumber, Row, Col, Button, message } from "antd";
import api from "../api/axios";

const Settings = () => {

  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchSettings = async () => {

    try {

      const res = await api.get("/settings");
      setSettings(res.data);

    } catch (err) {

      console.error("Settings load failed", err);
      message.error("Failed to load settings");

    }

  };

  useEffect(() => {

    fetchSettings();

  }, []);

  const updateSettings = async () => {

    try {

      setLoading(true);

      await api.put("/settings", settings);

      message.success("Settings updated");

    } catch (err) {

      message.error("Update failed");

    } finally {

      setLoading(false);

    }

  };

  return (

    <div className="page-container">

      {/* ---------------------- */}
      {/* AUTOMATION SETTINGS */}
      {/* ---------------------- */}

      <Card title="Automation Settings" className="app-card" style={{ marginBottom:20 }}>

        <Row gutter={16}>

          <Col span={12}>
            Auto Generate Draft
          </Col>

          <Col span={12}>
            <Switch
              checked={settings.auto_generate_draft}
              onChange={(v) =>
                setSettings({...settings, auto_generate_draft:v})
              }
            />
          </Col>

        </Row>

        <Row gutter={16} style={{ marginTop:15 }}>

          <Col span={12}>
            Auto Generate Risk
          </Col>

          <Col span={12}>
            <Switch
              checked={settings.auto_generate_risk}
              onChange={(v) =>
                setSettings({...settings, auto_generate_risk:v})
              }
            />
          </Col>

        </Row>

        <Row gutter={16} style={{ marginTop:15 }}>

          <Col span={12}>
            Auto Assign High Risk
          </Col>

          <Col span={12}>
            <Switch
              checked={settings.auto_assign_high_risk}
              onChange={(v) =>
                setSettings({...settings, auto_assign_high_risk:v})
              }
            />
          </Col>

        </Row>

        <Row gutter={16} style={{ marginTop:15 }}>

          <Col span={12}>
            High Risk Threshold
          </Col>

          <Col span={12}>
            <InputNumber
              min={1}
              max={5}
              value={settings.high_risk_threshold}
              onChange={(v)=>
                setSettings({...settings, high_risk_threshold:v})
              }
            />
          </Col>

        </Row>

      </Card>


      {/* ---------------------- */}
      {/* SLA SETTINGS */}
      {/* ---------------------- */}

      <Card title="SLA Settings" className="app-card" style={{ marginBottom:20 }}>

        <Row gutter={16}>

          <Col span={12}>
            Draft SLA (days)
          </Col>

          <Col span={12}>
            <InputNumber
              min={1}
              value={settings.draft_sla_days}
              onChange={(v)=>
                setSettings({...settings, draft_sla_days:v})
              }
            />
          </Col>

        </Row>

        <Row gutter={16} style={{ marginTop:15 }}>

          <Col span={12}>
            Review SLA (days)
          </Col>

          <Col span={12}>
            <InputNumber
              min={1}
              value={settings.review_sla_days}
              onChange={(v)=>
                setSettings({...settings, review_sla_days:v})
              }
            />
          </Col>

        </Row>

        <Row gutter={16} style={{ marginTop:15 }}>

          <Col span={12}>
            Submission SLA (days)
          </Col>

          <Col span={12}>
            <InputNumber
              min={1}
              value={settings.submission_sla_days}
              onChange={(v)=>
                setSettings({...settings, submission_sla_days:v})
              }
            />
          </Col>

        </Row>

      </Card>


      <Button
        type="primary"
        onClick={updateSettings}
        loading={loading}
      >
        Save Settings
      </Button>

    </div>

  );

};

export default Settings;