import { Card, Form, Input, Button, message } from "antd";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

const Login = () => {
  const navigate = useNavigate();

  const onFinish = async (values) => {
  try {
    const response = await api.post("/login", null, {
      params: {
        email: values.email,
        password: values.password,
      },
    });

    localStorage.setItem("access_token", response.data.access_token);

        message.success("Login successful");
        navigate("/");
    } catch (error) {
        message.error("Invalid credentials");
    }
    };

  return (
    <div style={{ display: "flex", height: "100vh", justifyContent: "center", alignItems: "center" }}>
      <Card title="TaxCopilot Login" style={{ width: 350 }}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="Email" name="email" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item label="Password" name="password" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>

          <Button type="primary" htmlType="submit" block>
            Login
          </Button>
        </Form>
      </Card>
    </div>
  );
};

export default Login;