import { test, expect } from "@playwright/test";

import { ADMIN, ADMIN_DISPLAY_NAME } from "./admin";
import { login, createTask } from "./helpers";

test("detail page shows priority and drives status through legal transitions", async ({
  page,
}) => {
  await login(page, ADMIN);
  await createTask(page, {
    title: `detail ${Date.now()}`,
    assigneeLabel: ADMIN_DISPLAY_NAME,
    priority: "high",
  });

  await expect(page.getByText("Độ ưu tiên")).toBeVisible();
  await expect(page.getByText("Cao")).toBeVisible();

  const status = page.getByRole("combobox", { name: "Đổi trạng thái" });
  await expect(status).toHaveValue("new");

  // new → in_progress is the only legal step; done must not be offered yet.
  await expect(status.getByRole("option")).toHaveText(["Mới", "Đang xử lý"]);

  await status.selectOption("in_progress");
  await expect(status).toHaveValue("in_progress");
  await expect(page.getByText("Bắt đầu")).toBeVisible();

  await status.selectOption("done");
  await expect(status).toHaveValue("done");
  // done is terminal: the control locks.
  await expect(status).toBeDisabled();
  await expect(
    page.locator("dt").filter({ hasText: /^Hoàn thành$/ }),
  ).toBeVisible();
});
