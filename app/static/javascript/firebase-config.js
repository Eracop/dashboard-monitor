// firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.5.2/firebase-app.js";
import firebase from "firebase/compat/app";
// Required for side-effects
import "firebase/firestore";
// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAosin-9_jU4XjeO5Wzxuo9eggVbfZ8C7g",
  authDomain: "todolist-4d00b.firebaseapp.com",
  projectId: "todolist-4d00b",
  storageBucket: "todolist-4d00b.appspot.com",
  messagingSenderId: "626634862526",
  appId: "1:626634862526:web:1b65bb3d9c06606c7853ef",
  measurementId: "G-STTBBXDPE6"
};

export const app = initializeApp(firebaseConfig);
