<script>
  import { foodEntries, sleepEntries } from "./stores";
  import { formatForCopy } from "./utils";

  let inputText = "";
  if ($foodEntries[0] && $sleepEntries[0]) {
    inputText = `Lio heeft heet laatst gegeten om ${formatForCopy($foodEntries[0].start)} en heeft geslapen tot ${formatForCopy($sleepEntries[0].end)}`;
  }

  console.log($foodEntries[0]);

  function copyToClipboard() {
    navigator.clipboard.writeText(inputText);
  }

  function sync() {
    alert("Syncing...");
  }
</script>

<div class="container">
  <div class="row mb-2 mt-4 justify-content-center">
    <div class="col-lg-8">
      <div class="card">
        <div class="card-body">
          <div class="row">
            <div class="col">
              <textarea
                type="text"
                class="form-control mb-2"
                rows="8"
                bind:value={inputText}
              />
              <button class="btn btn-primary w-100" on:click={copyToClipboard}>
                Copy to Clipboard
              </button>
            </div>
            <div class="col">
              <button class="btn btn-primary w-100 h-100" on:click={sync}>
                Sync
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
