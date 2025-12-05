import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthContextProvider, AuthContext } from './context/AuthContext';
import App from './App';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import NavbarComponent from './components/NavBar';
import { MovieContextProvider } from './context/MovieContext';
import { EventsContextProvider } from './context/EventsContext';

function Root() {
  const auth = React.useContext(AuthContext);

  return (
    <>
      {auth?.user && <NavbarComponent />}
      <App />
    </>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthContextProvider>
        <MovieContextProvider>
          <EventsContextProvider>
            <Root />
          </EventsContextProvider>
        </MovieContextProvider>
      </AuthContextProvider>
    </BrowserRouter>
  </React.StrictMode>
);
