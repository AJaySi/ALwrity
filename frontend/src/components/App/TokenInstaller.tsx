import { useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { setAuthTokenGetter, setClerkSignOut } from '../../api/client';
import { setMediaAuthTokenGetter } from '../../utils/fetchMediaBlobUrl';
import { setBillingAuthTokenGetter } from '../../services/billingService';

const TokenInstaller: React.FC = () => {
  const { getToken, userId, isSignedIn, signOut } = useAuth();
  
  useEffect(() => {
    if (isSignedIn && userId) {
      console.log('TokenInstaller: Storing user_id in localStorage:', userId);
      localStorage.setItem('user_id', userId);
      
      window.dispatchEvent(new CustomEvent('user-authenticated', { detail: { userId } }));
    } else if (!isSignedIn) {
      console.log('TokenInstaller: Clearing user_id from localStorage');
      localStorage.removeItem('user_id');
    }
  }, [isSignedIn, userId]);
  
  useEffect(() => {
    const tokenGetter = async () => {
      try {
        const template = process.env.REACT_APP_CLERK_JWT_TEMPLATE;
        if (template && template !== 'your_jwt_template_name_here') {
          return await getToken({ template });
        }
        return await getToken();
      } catch {
        return null;
      }
    };
    
    setAuthTokenGetter(tokenGetter);
    setBillingAuthTokenGetter(tokenGetter);
    setMediaAuthTokenGetter(tokenGetter);
  }, [getToken]);
  
  useEffect(() => {
    if (signOut) {
      setClerkSignOut(async () => {
        await signOut();
      });
    }
  }, [signOut]);
  
  return null;
};

export default TokenInstaller;
