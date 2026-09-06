import './globals.css';

export const metadata = {
  title: '酒店价格比价器',
  description: '比较去哪儿、智行、高德的酒店价格',
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
