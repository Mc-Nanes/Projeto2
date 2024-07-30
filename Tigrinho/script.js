/**
 * Setup
 */
const debugEl = document.getElementById('debug'),
    // Mapping of indexes to icons: start from banana in middle of initial position and then upwards
    rollButton = document.getElementById('rollButton');
    saldoEl = document.getElementById('saldo')
    iconMap = ["ILHA", "IGLU", "AGENTE", "URSO", "BICHO FELIZ", "MESTRE", "BICHO PUTO", "PIRATA", "IDOSO"],
    // Width of the icons
    icon_width = 74,
    // Height of one icon in the strip
    icon_height = 78,
    // Number of icons in the strip
    num_icons = 9,
    // Max-speed in ms for animating one icon down
    time_per_icon = 100,
    // Holds icon indexes
    indexes = [0, 0, 0];

let saldo = 100;

// Deduct cost of roll
const deductCost = () => {
    saldo -= 10;
    updateSaldo();
};

// Add winnings
const addWinnings = (money) => {
    saldo += money;
    updateSaldo();
};

const updateSaldo = () =>{
    saldoEl.textContent = 'Saldo: R$' + saldo.toFixed(2);
}

/**
 * Roll one reel
 */
const roll = (reel, offset = 0) => {
    // Minimum of 2 + the reel offset rounds
    const delta = (offset + 2) * num_icons + Math.round(Math.random() * num_icons);

    // Return promise so we can wait for all reels to finish
    return new Promise((resolve, reject) => {
        const style = getComputedStyle(reel),
            // Current background position
            backgroundPositionY = parseFloat(style["background-position-y"]),
            // Target background position
            targetBackgroundPositionY = backgroundPositionY + delta * icon_height,
            // Normalized background position, for reset
            normTargetBackgroundPositionY = targetBackgroundPositionY % (num_icons * icon_height);

        // Delay animation with timeout, for some reason a delay in the animation property causes stutter
        setTimeout(() => {
            // Set transition properties ==> https://cubic-bezier.com/#.41,-0.01,.63,1.09
            reel.style.transition = `background-position-y ${(8 + 1 * delta) * time_per_icon}ms cubic-bezier(.41,-0.01,.63,1.09)`;
            // Set background position
            reel.style.backgroundPositionY = `${targetBackgroundPositionY}px`;
        }, offset * 150);

        // After animation
        setTimeout(() => {
            // Reset position, so that it doesn't get higher without limit
            reel.style.transition = `none`;
            reel.style.backgroundPositionY = `${normTargetBackgroundPositionY}px`;
            // Resolve this promise
            resolve(delta % num_icons);
        }, (8 + 1 * delta) * time_per_icon + offset * 150);
    });
};

/**
 * Roll all reels, when promise resolves roll again
 */
function rollAll() {
    if(saldo < 10){
        alert("Saldo Insuficiente");
        return;
    }
    rollButton.disabled = true;
    deductCost();
    debugEl.textContent = 'rolling...';

    const reelsList = document.querySelectorAll('.slots > .reel');

    Promise
        // Activate each reel, must convert NodeList to Array for this with spread operator
        .all([...reelsList].map((reel, i) => roll(reel, i)))
        // When all reels done animating (all promises solve)
        .then((deltas) => {
            // add up indexes
            deltas.forEach((delta, i) => indexes[i] = (indexes[i] + delta) % num_icons);
            //debugEl.textContent = indexes.map((i) => iconMap[i]).join(' - ');

            // Win conditions
            if (indexes[0] == indexes[1] || indexes[1] == indexes[2]) {
                const winCls = indexes[0] == indexes[2] ? "win2" : "win1";
                if (winCls == "win1"){
                    addWinnings(30)
                } else {
                    addWinnings(50)
                }
                document.querySelector(".slots").classList.add(winCls);
                setTimeout(() => document.querySelector(".slots").classList.remove(winCls), 2000);
            }

            // Again!
            //setTimeout(rollAll, 3000);
            rollButton.disabled = false;
        });
};

// Add event listener to the button
rollButton.addEventListener('click', rollAll);
//Add balance display
updateSaldo();