import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

// TODO: Replace with your Firebase project configuration
const firebaseConfig = {
  apiKey: "AIzaSyBlt7YTBhoPbSE0lPXQtlX9oritLKhMtTM",
  authDomain: "gen-lang-client-0954319650.firebaseapp.com",
  projectId: "gen-lang-client-0954319650",
  storageBucket: "gen-lang-client-0954319650.firebasestorage.app",
  messagingSenderId: "159401423843",
  appId: "1:159401423843:web:8fdc07768c5533eb5366d6"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// Provider with Drive scope
export const provider = new GoogleAuthProvider();
provider.addScope('https://www.googleapis.com/auth/drive.readonly');

export { signInWithPopup, signOut };



 
