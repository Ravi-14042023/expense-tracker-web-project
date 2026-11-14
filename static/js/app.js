// Mobile menu (hamburger button + slide-in sidebar)
(function () {
  const sidebar = document.getElementById("sidebar");
  const menuToggle = document.getElementById("menuToggle");
  const overlay = document.getElementById("sidebarOverlay");

  if (!sidebar || !menuToggle || !overlay) return;

  function setMenu(open) {
    sidebar.classList.toggle("open", open);
    document.body.classList.toggle("nav-open", open);
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  menuToggle.addEventListener("click", () => {
    setMenu(!sidebar.classList.contains("open"));
  });

  // Close when tapping the dark area, pressing Escape, or choosing a page.
  overlay.addEventListener("click", () => setMenu(false));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenu(false);
  });

  sidebar.querySelectorAll("nav a").forEach((link) => {
    link.addEventListener("click", () => setMenu(false));
  });

  // If the window grows back to desktop size, reset the menu state.
  window.matchMedia("(min-width: 901px)").addEventListener("change", (event) => {
    if (event.matches) setMenu(false);
  });
})();

const toggleButton = document.getElementById("toggle-calculator");
const calculator = document.getElementById("calculator");
const display = document.getElementById("calc-display");
const amountInput = document.getElementById("amount");
const errorMessage = document.getElementById("calc-error");

if (toggleButton && calculator && display) {
  toggleButton.addEventListener("click", () => {
    calculator.hidden = !calculator.hidden;
  });

  document.querySelectorAll("[data-value]").forEach((button) => {
    button.addEventListener("click", () => {
      display.value += button.dataset.value;
      errorMessage.textContent = "";
    });
  });

  document.getElementById("calc-clear").addEventListener("click", () => {
    display.value = "";
    errorMessage.textContent = "";
  });

  function calculateExpression() {
    const expression = display.value.trim();

    // Accept only numbers, decimal points and basic arithmetic.
    if (!expression || !/^[\d+\-*/().\s]+$/.test(expression)) {
      throw new Error("Enter a valid arithmetic expression.");
    }

    // Evaluate a restricted arithmetic expression.
    const result = Function('"use strict"; return (' + expression + ")")();

    if (typeof result !== "number" || !Number.isFinite(result)) {
      throw new Error("The result is not a valid number.");
    }

    return result;
  }

  document.getElementById("calc-equals").addEventListener("click", () => {
    try {
      display.value = String(calculateExpression());
      errorMessage.textContent = "";
    } catch (error) {
      errorMessage.textContent = error.message;
    }
  });

  document.getElementById("use-result").addEventListener("click", () => {
    try {
      const result = calculateExpression();

      if (result <= 0) {
        throw new Error("Amount must be greater than zero.");
      }

      amountInput.value = result.toFixed(2);
      calculator.hidden = true;
      errorMessage.textContent = "";
    } catch (error) {
      errorMessage.textContent = error.message;
    }
  });
}

const expenseModal = document.getElementById("expenseModal");

const openExpenseButtons = [
  document.getElementById("openExpenseForm"),
  document.getElementById("openExpenseFormEmpty"),
];

openExpenseButtons.forEach((button) => {
  if (button && expenseModal) {
    button.addEventListener("click", () => {
      expenseModal.hidden = false;

      expenseModal.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }
});

const closeExpenseButton = document.getElementById("closeExpenseForm");

if (closeExpenseButton && expenseModal) {
  closeExpenseButton.addEventListener("click", () => {
    expenseModal.hidden = true;
  });
}

const openNewCategoryButton = document.getElementById("openNewCategory");

const newCategoryForm = document.getElementById("newCategoryForm");

if (openNewCategoryButton && newCategoryForm) {
  openNewCategoryButton.addEventListener("click", () => {
    newCategoryForm.hidden = !newCategoryForm.hidden;
  });
}
// Set monthly chart bar heights
document.querySelectorAll(".month-bar").forEach((bar) => {
  const height = Number(bar.dataset.height) || 0;
  bar.style.height = `${height}%`;
});

const pieChart = document.getElementById("categoryPieChart");
const legendLeft = document.getElementById("categoryPieLegendLeft");
const legendRight = document.getElementById("categoryPieLegendRight");

if (pieChart && legendLeft && legendRight) {
  const colors = [
    "#6366f1",
    "#14b8a6",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#ec4899",
    "#84cc16",
    "#f97316",
    "#64748b",
  ];

  const items = [
    ...legendLeft.querySelectorAll(".pie-legend-item"),
    ...legendRight.querySelectorAll(".pie-legend-item"),
  ];

  const total = items.reduce((sum, item) => {
    return sum + (Number(item.dataset.amount) || 0);
  }, 0);

  let currentAngle = 0;
  const slices = [];

  items.forEach((item, index) => {
    const amount = Number(item.dataset.amount) || 0;
    const percentage = total > 0 ? (amount / total) * 100 : 0;
    const nextAngle = currentAngle + percentage * 3.6;
    const color = colors[index % colors.length];

    slices.push(`${color} ${currentAngle}deg ${nextAngle}deg`);

    const colorMarker = item.querySelector(".pie-color");
    colorMarker.style.backgroundColor = color;

    const percentageLabel = item.querySelector(".pie-percentage");
    percentageLabel.textContent = `${percentage.toFixed(1)}%`;

    currentAngle = nextAngle;
  });

  pieChart.style.background =
    total > 0 ? `conic-gradient(${slices.join(", ")})` : "#e5e7eb";
}
document.querySelectorAll(".flash-message").forEach((message) => {
  setTimeout(() => {
    message.remove();
  }, 4000);
});

document.querySelectorAll(".note-preview").forEach((note) => {
  note.addEventListener("click", (event) => {
    event.stopPropagation();

    const isExpanded = note.classList.contains("expanded");

    document.querySelectorAll(".note-preview.expanded").forEach((item) => {
      item.classList.remove("expanded");
      item.setAttribute("aria-expanded", "false");
    });

    if (!isExpanded) {
      note.classList.add("expanded");
      note.setAttribute("aria-expanded", "true");
    }
  });

  note.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      note.click();
    }
  });
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".note-preview.expanded")) {
    document.querySelectorAll(".note-preview.expanded").forEach((note) => {
      note.classList.remove("expanded");
      note.setAttribute("aria-expanded", "false");
    });
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    document.querySelectorAll(".note-preview.expanded").forEach((note) => {
      note.classList.remove("expanded");
      note.setAttribute("aria-expanded", "false");
    });
  }
});

document.querySelectorAll(".toast-message").forEach((toast) => {
  setTimeout(() => {
    toast.remove();
  }, 4000);
});

document.addEventListener("DOMContentLoaded", function () {
  const viewButtons = document.querySelectorAll(".view-button");
  const summaryViews = document.querySelectorAll(".expense-summary-view");
  const originalTable = document.querySelector(".original-expense-table");
  const allExpensesButton = document.getElementById("show-all-expenses");

  viewButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const selectedView = button.dataset.view;

      // Hide all summary views.
      summaryViews.forEach(function (view) {
        view.hidden = true;
      });

      // Show the selected summary.
      const viewIds = {
        category: "category-view",
        monthly: "monthly-view",
        "monthly-category": "monthly-category-view",
      };

      const targetView = document.getElementById(viewIds[selectedView]);

      if (targetView) {
        targetView.hidden = false;
      }

      // Hide the original expense table.
      if (originalTable) {
        originalTable.hidden = true;
      }

      // Update the selected button.
      viewButtons.forEach(function (item) {
        item.classList.remove("active");
      });

      button.classList.add("active");
    });
  });

  // Handle the All Expenses button.
  if (allExpensesButton) {
    allExpensesButton.addEventListener("click", function () {
      // Hide all summary views.
      summaryViews.forEach(function (view) {
        view.hidden = true;
      });

      // Show the original expense table.
      if (originalTable) {
        originalTable.hidden = false;
      }

      // Update button styles.
      viewButtons.forEach(function (item) {
        item.classList.remove("active");
      });

      allExpensesButton.classList.add("active");
    });
  }
});
