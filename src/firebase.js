// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from 'firebase/firestore';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

export const db_table = "dev_entries";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAmuuaqvpBpsArvvRIRutZSBdEJfa40BK8",
  authDomain: "babytracker-b2323.firebaseapp.com",
  projectId: "babytracker-b2323",
  storageBucket: "babytracker-b2323.appspot.com",
  messagingSenderId: "847885705138",
  appId: "1:847885705138:web:e40d62079a600541caceab"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export const db = getFirestore(app);

auth.onAuthStateChanged(function (user) {
  console.log('auth state changed');
  if (user) {
    db.collection('users').doc(user.uid).get().then((docSnapshot) => {
      if (!docSnapshot.exists) {
        console.log(user.uid);
        db.collection('users').doc(user.uid).set({});
      }
    });
  }
});