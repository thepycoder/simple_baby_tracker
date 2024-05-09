<script>
  import { formatTime, convertToDatetimeLocal } from "./utils";
  import { onMount } from "svelte";
  import { db, db_table } from "./firebase";
  import {
    updateDoc,
    doc,
    serverTimestamp,
    query,
    collection,
    orderBy,
    limit,
    onSnapshot,
    addDoc,
  } from "firebase/firestore";
  import { sleepEntries } from "./stores";

  let sleepStart, currentSleepDocId;
  let isSleeping = false;
  let clockSleepInterval;
  let sleepDuration = 0;
  let lastSleepEnd;
  let sleepSinceLast = "N/A";

  function startSleep() {
    const startTimestamp = serverTimestamp();
    sleepStart = new Date();
    isSleeping = true;
    addDoc(collection(db, db_table), {
      type: "sleep",
      start: startTimestamp,
    }).then((docRef) => {
      currentSleepDocId = docRef.id;
      startSleepClock();
    });
  }

  function endSleep() {
    const endTimestamp = serverTimestamp();
    if (currentSleepDocId) {
      updateDoc(doc(db, db_table, currentSleepDocId), {
        end: endTimestamp,
      }).then(() => {
        lastSleepEnd = new Date();
        resetSleep();
        updateSleepSinceLast();
      });
    }
  }

  function updateSleepSinceLastNow() {
    const now = new Date();
    sleepSinceLast = formatTime(now - lastSleepEnd);
  }

  function updateSleepSinceLast() {
    if (lastSleepEnd) {
      updateSleepSinceLastNow();
      const interval = setInterval(updateSleepSinceLastNow, 1000);
      // onDestroy(() => clearInterval(interval));
    }
  }

  function resetSleep() {
    isSleeping = false;
    stopSleepClock();
  }

  function startSleepClock() {
    clearInterval(clockSleepInterval);
    clockSleepInterval = setInterval(updateSleepDuration, 1000);
  }

  function updateSleepDuration() {
    if (isSleeping) {
      const now = new Date();
      const elapsed = now - sleepStart;
      sleepDuration = Math.floor(elapsed);
    }
  }

  function stopSleepClock() {
    clearInterval(clockSleepInterval);
    sleepDuration = 0;
  }

  $: $sleepEntries, init();

  function init() {
    // Initialize latest end times
    const lastSleep = $sleepEntries[0];

    if (lastSleep) {
      isSleeping = !Boolean(lastSleep.end);
      if (lastSleep.end) {
        lastSleepEnd = lastSleep.end;
        updateSleepSinceLast();
      } else {
        currentSleepDocId = lastSleep.id;
        sleepStart = lastSleep.start;
        startSleepClock();
      }
    }
  }
</script>

{#if isSleeping}
  <p class="text-muted text-center mt-2">
    Tijd sinds start slaapje: <b class="fs-2">{formatTime(sleepDuration)}</b>
  </p>
  <button on:click={endSleep} class="btn btn-danger w-100 mt-2"
    >Stop Slaapje</button
  >
{:else}
  <div class="card mt-4 border-success">
    <div class="row g-0">
      <div class="col-6 d-flex align-items-center">
        <h2 class="card-text text-center display-5 fw-bold m-0 w-100">
          {sleepSinceLast}
        </h2>
      </div>
      <div class="col-6 bg-success">
        <button
          on:click={startSleep}
          class="btn btn-success w-100 h-100"
          disabled={isSleeping}
          ><i class="bi bi-moon-stars" style="font-size: 4em;"></i></button
        >
      </div>
    </div>
  </div>
{/if}
