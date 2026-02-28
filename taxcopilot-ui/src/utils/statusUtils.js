export const getStatusTag = (status) => {
  switch (status) {
    case "open":
      return { label: "Open", color: "blue" };

    case "in_progress":
      return { label: "In Progress", color: "orange" };

    case "replied":
      return { label: "Replied", color: "gold" };

    case "closed":
      return { label: "Closed", color: "green" };

    default:
      return { label: status, color: "default" };
  }
};