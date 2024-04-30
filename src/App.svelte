<!-- src/App.svelte -->
<script>
  import { db, db_table } from "./firebase";
  import {
    collection,
    addDoc,
    serverTimestamp,
    query,
    orderBy,
    onSnapshot,
    doc,
    updateDoc,
    limit,
    getDoc,
    deleteDoc,
  } from "firebase/firestore";
  import { formatTime, convertToDatetimeLocal } from "./utils";
  import { onMount, onDestroy } from "svelte";
  import { auth, googleProvider } from "./firebase";
  import { authState } from "rxfire/auth";
  import { signInWithPopup, signOut } from "firebase/auth";
  import ConfirmModal from "./ConfirmModal.svelte";
  import SleepEntry from "./SleepEntry.svelte";
  import FoodEntry from "./FoodEntry.svelte";
  import FoodInput from "./foodInput.svelte";

  let entries = [];

  let sleepStart, currentSleepDocId;
  let isSleeping = false;
  let clockSleepInterval;
  let sleepDuration = 0;
  let lastSleepEnd;
  let sleepSinceLast = "N/A";

  let user = "";

  const unsubscribe = authState(auth).subscribe((u) => (user = u));

  function login() {
    signInWithPopup(auth, googleProvider);
  }

  function logout() {
    signOut();
  }

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

  function updateSleepSinceLast() {
    if (lastSleepEnd) {
      const interval = setInterval(() => {
        const now = new Date();
        sleepSinceLast = formatTime(now - lastSleepEnd);
      }, 1000);
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
    clearInterval(clockFoodInterval);
    sleepDuration = 0;
  }

  onMount(() => {
    const q = query(
      collection(db, db_table),
      orderBy("start", "desc"),
      limit(10)
    );
    const unsubscribe = onSnapshot(q, (snapshot) => {
      entries = snapshot.docs.map((doc) => {
        const data = doc.data();
        return {
          id: doc.id,
          ...data,
          start: data.start.toDate(),
          edit_start: convertToDatetimeLocal(data.start.toDate()),
          end: data.end ? data.end.toDate() : null,
          edit_end: data.end ? convertToDatetimeLocal(data.end.toDate()) : null,
        };
      });
    });
  });

  // onMount(() => {
  //   const q = query(
  //     collection(db, db_table),
  //     orderBy("start", "desc"),
  //     limit(10)
  //   );
  //   const unsubscribe = onSnapshot(q, (snapshot) => {
  //     entries = snapshot.docs.map((doc) => {
  //       const data = doc.data();
  //       return {
  //         id: doc.id,
  //         ...data,
  //         start: data.start.toDate(),
  //         edit_start: convertToDatetimeLocal(data.start.toDate()),
  //         end: data.end ? data.end.toDate() : null,
  //         edit_end: data.end ? convertToDatetimeLocal(data.end.toDate()) : null,
  //       };
  //     });
  //     // Initialize latest end times
  //     const lastSleep = entries.find((e) => e.type === "sleep" && e.end);
  //     const lastFood = entries.find((e) => e.type === "food" && e.start);

  //     if (lastSleep) {
  //       lastSleepEnd = lastSleep.end;
  //       updateSleepSinceLast();
  //     }
  //     if (lastFood) {
  //       lastFoodStart.set(lastFood.start);
  //       updateFoodSinceLast();
  //     }
  //     // Update current activity states based on the latest entries
  //     updateCurrentActivities();
  //   });
  //   return () => unsubscribe();
  // });

  // function updateCurrentActivities() {
  //   let activeSleepEntry = entries.find(
  //     (entry) => entry.type === "sleep" && !entry.end
  //   );
  //   let activeFoodEntry = entries.find(
  //     (entry) => entry.type === "food" && !entry.end
  //   );

  //   if (activeSleepEntry) {
  //     currentSleepDocId = activeSleepEntry.id;
  //     sleepStart = activeSleepEntry.start;
  //     if (!isSleeping) {
  //       isSleeping = true;
  //       startSleepClock();
  //     }
  //   } else if (isSleeping) {
  //     isSleeping = false;
  //     stopSleepClock();
  //   }

  //   isEating.set(!!activeFoodEntry);
  //   if (activeFoodEntry) {
  //     currentFoodDocId.set(activeFoodEntry.id);
  //     foodStart.set(activeFoodEntry.start);
  //     startFoodClock();
  //   }
  // }

  let showModal = false;
  let entryIdToDelete = null;

  async function removeEntry(entryId) {
    try {
      await deleteDoc(doc(db, db_table, entryId));
      // Optionally add some UI feedback here, e.g., a toast notification
    } catch (error) {
      console.error("Error removing document: ", error);
      // Handle errors, e.g., show an error message to the user
    }
  }

  function requestDelete(entryId) {
    entryIdToDelete = entryId;
    showModal = true;
  }

  function handleConfirm() {
    removeEntry(entryIdToDelete);
    showModal = false;
    entryIdToDelete = null;
  }

  function handleCancel() {
    showModal = false;
    entryIdToDelete = null;
  }
</script>

<main class="container mt-5">
  <ConfirmModal
    show={showModal}
    message="Are you sure you want to delete this entry?"
    on:confirm={handleConfirm}
    on:cancel={handleCancel}
  />
  {#if user}
    <!-- <h1 class="text-center mb-4">Lio's Activities Tracker</h1> -->
    <div class="row justify-content-center">
      <!-- Sleep input -->
      <section class="col-md-6 mb-3">
        {#if isSleeping}
          <p class="text-muted text-center mt-2">
            Tijd sinds start slaapje: <b class="fs-2"
              >{formatTime(sleepDuration)}</b
            >
          </p>
          <button on:click={endSleep} class="btn btn-danger w-100 mt-2"
            >Stop Sleep</button
          >
        {:else}
          <p class="text-muted text-center mt-2">
            Tijd sinds laatste slaapje: <b class="fs-2">{sleepSinceLast}</b>
          </p>
          <button
            on:click={startSleep}
            class="btn btn-primary w-100 mt-2"
            disabled={isSleeping}>Start Sleep</button
          >
        {/if}
      </section>
      <!-- Food input -->
      <section class="col-md-6 mb-3">
        <FoodInput {entries} />
      </section>
    </div>
    <div class="row justify-content-center">
      <!-- Latest Sleep entry -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "sleep").slice(0, 1) as entry}
          <SleepEntry {entry} latest={true} onDelete={requestDelete} />
        {/each}
      </div>
      <!-- Latest Food entry -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "food").slice(0, 1) as entry}
          <FoodEntry {entry} latest={true} onDelete={requestDelete} />
        {/each}
      </div>
    </div>
    <div class="row justify-content-center">
      <!-- All Sleep entries excluding the latest -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "sleep").slice(1) as entry}
          <SleepEntry {entry} latest={false} onDelete={requestDelete} />
        {/each}
      </div>
      <!-- All Food entries excluding the latest -->
      <div class="col-md-6">
        {#each entries.filter((e) => e.type === "food").slice(1) as entry}
          <FoodEntry {entry} latest={false} onDelete={requestDelete} />
        {/each}
      </div>
    </div>
  {:else}
    <div class="headerBar">
      <h1 class="header top">Victor's baby tracker!</h1>
      <button on:click={login} class="btn btn-primary"
        >Sign in with google</button
      >
    </div>
  {/if}
</main>
