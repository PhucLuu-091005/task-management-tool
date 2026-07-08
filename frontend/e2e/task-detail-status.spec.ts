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

  const status = page.getByRole("button", { name: "Đổi trạng thái" });
  await expect(status).toContainText("Mới");

  await status.click();
  // new → in_progress is the only legal step; "Hoàn thành" must not be offered yet.
  await expect(page.getByRole("menuitem")).toHaveText(["Đang xử lý"]);
  await page.getByRole("menuitem", { name: "Đang xử lý" }).click();
  await page.getByRole("button", { name: "Chuyển" }).click();
  await expect(status).toContainText("Đang xử lý");
  await expect(page.getByText("Bắt đầu")).toBeVisible();

  await status.click();
  await page.getByRole("menuitem", { name: "Hoàn thành" }).click();
  await page.getByRole("button", { name: "Chuyển" }).click();

  // done is terminal: the pill becomes a plain, non-interactive badge.
  await expect(page.getByRole("button", { name: "Đổi trạng thái" })).toHaveCount(0);
  await expect(
    page.locator("dt").filter({ hasText: /^Hoàn thành$/ }),
  ).toBeVisible();
});
