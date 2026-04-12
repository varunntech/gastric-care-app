import { createContext, useContext, useEffect, useState } from 'react';
import { 
  onAuthStateChanged, 
  signInWithPopup, 
  GoogleAuthProvider, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  updateProfile
} from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db } from './firebase';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      if (currentUser) {
        // Fetch custom user profile from Firestore if needed
        const userDocRef = doc(db, 'users', currentUser.uid);
        const userDocSnap = await getDoc(userDocRef);
        
        let userData = {
          uid: currentUser.uid,
          email: currentUser.email,
          name: currentUser.displayName || 'User',
        };

        if (userDocSnap.exists()) {
          userData = { ...userData, ...userDocSnap.data() };
        } else {
          // If the document doesn't exist (e.g., first time Google Login), create it
          await setDoc(userDocRef, userData);
        }

        setUser(userData);
        setToken(await currentUser.getIdToken());
        
        // Also keep localStorage in sync for the Flask backend simple redirect if needed
        localStorage.setItem('token', await currentUser.getIdToken());
        localStorage.setItem('user', JSON.stringify(userData));
      } else {
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const loginProvider = new GoogleAuthProvider();

  const loginWithGoogle = async () => {
    const result = await signInWithPopup(auth, loginProvider);
    return result.user;
  };

  const loginWithEmail = async (email, password) => {
    const result = await signInWithEmailAndPassword(auth, email, password);
    return result.user;
  };

  const signupWithEmail = async (name, surname, email, password) => {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    await updateProfile(result.user, { displayName: `${name} ${surname}`.trim() });
    
    // Save to Firestore
    await setDoc(doc(db, 'users', result.user.uid), {
      uid: result.user.uid,
      email: result.user.email,
      name: `${name} ${surname}`.trim(),
      surname: surname
    });
    
    return result.user;
  };

  const logout = async () => {
    await signOut(auth);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      loginWithGoogle, 
      loginWithEmail, 
      signupWithEmail, 
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
