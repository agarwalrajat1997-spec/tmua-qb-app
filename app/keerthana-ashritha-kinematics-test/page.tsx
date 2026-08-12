export const metadata = {
  title: "ICSE Grade 9 Kinematics Mastery Challenge | Thriving Scholars",
  description:
    "90-minute interactive ICSE Grade 9 Motion in One Dimension assessment for Keerthana and Ashritha.",
};

export default function KinematicsTestPage() {
  return (
    <main style={{ margin: 0, width: "100%", minHeight: "100vh", background: "#fff" }}>
      <iframe
        src="/tools/keerthana-ashritha-kinematics/keerthana-ashritha-icse-kinematics.html"
        title="ICSE Grade 9 Kinematics Mastery Challenge"
        style={{
          display: "block",
          width: "100%",
          height: "100vh",
          border: 0,
        }}
        allow="fullscreen"
      />
    </main>
  );
}
