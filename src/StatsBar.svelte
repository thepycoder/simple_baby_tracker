<script>
  import {
    getFirestore,
    collection,
    query,
    where,
    getDocs,
    onSnapshot,
  } from "firebase/firestore";
  import { onMount, onDestroy } from "svelte";
  import { db, db_table } from "./firebase";
  import { convertToDatetimeLocal, formatTime } from "./utils";

  let numberSleep24h;
  let timeSlept24h;
  let numberFood24h;
  let timeFed24h;

  onMount(() => {
    const now = new Date();
    const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const s24q = query(
      collection(db, db_table),
      where("type", "==", "sleep"),
      where("end", ">=", twentyFourHoursAgo)
    );
    const s24_unsubscribe = onSnapshot(s24q, (snapshot) => {
      timeSlept24h = 0;
      snapshot.docs.map((doc) => {
        const data = doc.data();
        timeSlept24h += data.end.toDate() - data.start.toDate();
      });
      numberSleep24h = snapshot.docs.length;
    });

    const f24q = query(
      collection(db, db_table),
      where("type", "==", "food"),
      where("end", ">=", twentyFourHoursAgo)
    );
    const f24_unsubscribe = onSnapshot(f24q, (snapshot) => {
      timeFed24h = 0;
      snapshot.docs.map((doc) => {
        const data = doc.data();
        timeFed24h += data.end.toDate() - data.start.toDate();
      });
      numberFood24h = snapshot.docs.length;
    });

    return () => {
      s24_unsubscribe();
      f24_unsubscribe();
    };
  });
</script>

<div class="col-md-3 mb-2 text-center">
  <div class="card text-white bg-success">
    <h5 class="card-header">Tijd geslapen laatste 24u</h5>
    <div class="card-body">
      <h1>{formatTime(timeSlept24h)}</h1>
    </div>
  </div>
</div>
<div class="col-md-3 text-center">
  <div class="card text-white bg-primary">
    <h5 class="card-header">Aantal Voedingen 24u</h5>
    <div class="card-body">
      <h1 class="mb-2">{numberFood24h}</h1>
    </div>
  </div>
</div>
