import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyBFqQd-quDrhriBFsF2CpOVttuekzK_QGY",
  authDomain: "gastric-care.firebaseapp.com",
  projectId: "gastric-care",
  storageBucket: "gastric-care.firebasestorage.app",
  messagingSenderId: "542420375187",
  appId: "1:542420375187:web:db77e9f0b3f5da1e959f66"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
