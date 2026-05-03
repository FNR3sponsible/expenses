import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div style={{ padding: '20px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h1>Welcome, {username}!</h1>
        <button onClick={handleLogout}>Logout</button>
      </header>

      {role === 'parent' ? (
        <section>
          <h2>Parental Control Center</h2>
          <p>Monitor your child's spending and wishlist.</p>
          {/* Add Parent-specific components here */}
        </section>
      ) : (
        <section>
          <h2>Teen Savings Hub</h2>
          <p>Check your pocket money balance and wishlist progress.</p>
          {/* Add Teen-specific components here */}
        </section>
      )}
    </div>
  );
};

export default Dashboard;