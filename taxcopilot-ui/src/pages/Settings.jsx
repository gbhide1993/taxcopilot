import { useEffect, useState } from "react";
import { Switch, Card, message } from "antd";
import axios from "axios";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    const res = await axios.get("http://localhost:8000/settings");
    setSettings(res.data);
  };

  const handleToggle = async (checked) => {
    setLoading(true);
    try {
      const res = await axios.put("http://localhost:8000/settings", {
        auto_generate_draft: checked,
        auto_generate_risk: settings.auto_generate_risk
      });

      setSettings(res.data);
      message.success("Settings updated successfully");
    } catch (err) {
      message.error("Failed to update settings");
    }
    setLoading(false);
  };

  if (!settings) return null;

  return (
    <Card title="Automation Settings">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span>Auto Generate Draft on Upload</span>
        <Switch
          checked={settings.auto_generate_draft}
          onChange={handleToggle}
          loading={loading}
        />
      </div>
    </Card>
  );
}