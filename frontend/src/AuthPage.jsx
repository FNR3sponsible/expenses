import { useNavigate } from 'react-router-dom';

const AuthPage = () => {
  const navigate = useNavigate(); // Hook for navigation

  const handleSubmit = async (e) => {
    e.preventDefault();
    // ... your existing fetch logic ...

    if (response.ok) {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role); // Save role for dashboard logic
      
      // THIS IS THE KEY LINE:
      navigate('/dashboard'); 
    }
  };
  // ... rest of component
}