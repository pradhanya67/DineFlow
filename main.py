"""DineFlow — Smart Restaurant Operations Management System."""
from __future__ import annotations
from pathlib import Path
import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
import database as db

ctk.set_appearance_mode('dark'); ctk.set_default_color_theme('dark-blue')
BG='#121212'; SIDE='#1c1c1c'; CARD='#242424'; GOLD='#d4af37'; TEXT='#ffffff'; MUTED='#bdbdbd'; GREEN='#167a42'; RED='#a93636'; AMBER='#b98514'

class DineFlow(ctk.CTk):
    def __init__(self):
        super().__init__();db.initialize();self.title('DineFlow | Smart Restaurant Operations');self.geometry('1480x900');self.minsize(1120,700);self.configure(fg_color=BG);self.cart={};self.role='Customer';self.food_images=[];self.style();self.sidebar=ctk.CTkFrame(self,width=230,fg_color=SIDE,corner_radius=0);self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False);self.body=ctk.CTkFrame(self,fg_color=BG,corner_radius=0);self.body.pack(side='right',fill='both',expand=True);self.build_side();self.customer()
    def style(self):
        s=ttk.Style();s.theme_use('clam');s.configure('Treeview',background=CARD,fieldbackground=CARD,foreground=TEXT,rowheight=30,font=('Segoe UI',10));s.configure('Treeview.Heading',background='#303030',foreground=GOLD,font=('Segoe UI',10,'bold'));s.map('Treeview',background=[('selected','#59491c')])
    def build_side(self):
        for w in self.sidebar.winfo_children():w.destroy()
        ctk.CTkLabel(self.sidebar,text='♨  DineFlow',font=('Segoe UI',26,'bold'),text_color=GOLD).pack(anchor='w',padx=20,pady=(28,3));ctk.CTkLabel(self.sidebar,text='RESTAURANT MANAGEMENT',font=('Segoe UI',10,'bold'),text_color=MUTED).pack(anchor='w',padx=24,pady=(0,28))
        links=[('⌂  Customer Menu',self.customer),('▦  Admin Dashboard',self.admin),('♨  Kitchen Queue',self.kitchen),('♙  Waiter Service',self.waiter),('▣  Billing & Cashier',self.billing)]
        for label,cmd in links:ctk.CTkButton(self.sidebar,text=label,anchor='w',height=44,corner_radius=8,fg_color='transparent',hover_color='#383016',text_color=TEXT,font=('Segoe UI',14,'bold'),command=cmd).pack(fill='x',padx=12,pady=4)
        ctk.CTkLabel(self.sidebar,text='OFFLINE • SQLite • LOCAL',text_color=MUTED,font=('Segoe UI',10)).pack(side='bottom',pady=24)
    def clear(self):
        for w in self.body.winfo_children():w.destroy()
    def header(self,title,subtitle):
        h=ctk.CTkFrame(self.body,height=88,fg_color='#171717',corner_radius=0);h.pack(fill='x');h.pack_propagate(False);ctk.CTkLabel(h,text=title,font=('Segoe UI',25,'bold'),text_color=TEXT).place(x=30,y=17);ctk.CTkLabel(h,text=subtitle,font=('Segoe UI',12),text_color=MUTED).place(x=31,y=52);ctk.CTkLabel(h,text='●  Offline system active',font=('Segoe UI',12,'bold'),text_color=GREEN).place(relx=.80,y=34)
    def button(self,p,text,cmd,fg=GOLD,**kw):return ctk.CTkButton(p,text=text,command=cmd,fg_color=fg,hover_color='#b58c22',text_color='#16120a',font=('Segoe UI',12,'bold'),corner_radius=8,**kw)
    def card(self,p,title,value,color=GOLD):
        f=ctk.CTkFrame(p,fg_color=CARD,corner_radius=12);ctk.CTkLabel(f,text=title.upper(),text_color=MUTED,font=('Segoe UI',10,'bold')).pack(anchor='w',padx=16,pady=(15,2));ctk.CTkLabel(f,text=str(value),text_color=color,font=('Segoe UI',26,'bold')).pack(anchor='w',padx=16,pady=(0,14));return f
    def food_image(self, filename):
        try:
            path=Path(__file__).parent/'assets'/'food'/filename
            image=ctk.CTkImage(light_image=Image.open(path),dark_image=Image.open(path),size=(156,88));self.food_images.append(image);return image
        except Exception:return None
    def customer(self):
        self.clear();self.header('Order delicious food','Browse the menu, choose your table, and follow your order in real time.')
        root=ctk.CTkFrame(self.body,fg_color=BG);root.pack(fill='both',expand=True,padx=20,pady=16);root.grid_columnconfigure(0,weight=4);root.grid_columnconfigure(1,weight=2);root.grid_rowconfigure(1,weight=1)
        controls=ctk.CTkFrame(root,fg_color='transparent');controls.grid(row=0,column=0,sticky='ew',padx=(0,14));table=ctk.CTkOptionMenu(controls,values=[x['label'] for x in db.tables()],fg_color=CARD,button_color=GOLD,text_color=TEXT);table.set('T01');table.pack(side='left');name=ctk.CTkEntry(controls,placeholder_text='Customer name (optional)',width=190);name.pack(side='left',padx=8);search=ctk.CTkEntry(controls,placeholder_text='⌕  Search dishes...',width=220);search.pack(side='right')
        menu_box=ctk.CTkScrollableFrame(root,fg_color='#171717',corner_radius=12);menu_box.grid(row=1,column=0,sticky='nsew',padx=(0,14),pady=(12,0));cartbox=ctk.CTkFrame(root,fg_color=CARD,corner_radius=12);cartbox.grid(row=0,column=1,rowspan=2,sticky='nsew')
        catvar=ctk.StringVar(value='All');cats=ctk.CTkSegmentedButton(menu_box,values=db.categories(),variable=catvar,selected_color=GOLD,selected_hover_color='#b58c22',unselected_color='#333',command=lambda _:render());cats.pack(fill='x',padx=12,pady=12)
        grid=ctk.CTkFrame(menu_box,fg_color='transparent');grid.pack(fill='both',expand=True,padx=6);[grid.grid_columnconfigure(i,weight=1) for i in range(3)]
        def render(*_):
            for w in grid.winfo_children():w.destroy()
            for i,m in enumerate(db.menu(catvar.get(),search.get())):
                f=ctk.CTkFrame(grid,fg_color=CARD,corner_radius=10);f.grid(row=i//3,column=i%3,sticky='nsew',padx=6,pady=6);pic=self.food_image(m['image_path']);ctk.CTkLabel(f,text='' if pic else '◉',image=pic,text_color=GOLD,font=('Segoe UI',35)).pack(pady=(10,0));ctk.CTkLabel(f,text=m['name'],font=('Segoe UI',14,'bold')).pack();ctk.CTkLabel(f,text=m['description'],text_color=MUTED,wraplength=160,font=('Segoe UI',10)).pack(padx=7,pady=4);ctk.CTkLabel(f,text=db.money(m['price_paise']),text_color=GOLD,font=('Segoe UI',13,'bold')).pack();self.button(f,'+ Add',lambda x=m['id']:add(x),height=28).pack(fill='x',padx=10,pady=9)
        def add(mid):self.cart[mid]=self.cart.get(mid,0)+1;draw_cart()
        def draw_cart():
            for w in cartbox.winfo_children():w.destroy()
            ctk.CTkLabel(cartbox,text='Your Order',font=('Segoe UI',19,'bold'),text_color=TEXT).pack(anchor='w',padx=16,pady=(16,4));total=0
            for mid,q in self.cart.items():
                m=next(x for x in db.menu() if x['id']==mid);total+=m['price_paise']*q;row=ctk.CTkFrame(cartbox,fg_color='#303030',corner_radius=6);row.pack(fill='x',padx=12,pady=4);ctk.CTkLabel(row,text=f"{m['name']}\n{db.money(m['price_paise'])}",justify='left',font=('Segoe UI',11)).pack(side='left',padx=8,pady=6);ctk.CTkLabel(row,text=f'× {q}',text_color=GOLD).pack(side='right',padx=8)
            ctk.CTkLabel(cartbox,text=f'Subtotal     {db.money(total)}\nGST (5%)     {db.money(round(total*.05))}\nTotal         {db.money(round(total*1.05))}',justify='left',font=('Segoe UI',14,'bold'),text_color=TEXT).pack(anchor='w',padx=18,pady=16);notes=ctk.CTkEntry(cartbox,placeholder_text='Special instructions');notes.pack(fill='x',padx=12,pady=(0,10))
            def place():
                try:o=db.place_order(table.get(),name.get(),self.cart,notes.get());self.cart={};messagebox.showinfo('Order placed',f'{o} has been sent to the kitchen.');draw_cart();render()
                except Exception as e:messagebox.showerror('Cannot place order',str(e))
            self.button(cartbox,'Place Order',place,height=42).pack(side='bottom',fill='x',padx=12,pady=14)
        search.bind('<KeyRelease>',render);render();draw_cart()
    def admin(self):
        self.clear();self.header('Restaurant dashboard','Live table occupancy, pending orders, and revenue overview.')
        root=ctk.CTkFrame(self.body,fg_color=BG);root.pack(fill='both',expand=True,padx=22,pady=18);s=db.stats();stats=ctk.CTkFrame(root,fg_color='transparent');stats.pack(fill='x');[stats.grid_columnconfigure(i,weight=1) for i in range(6)]
        for i,(a,b,c) in enumerate([('Total tables',s['tables'],GOLD),('Available',s['available'],GREEN),('Occupied',s['occupied'],RED),('Reserved',s['reserved'],AMBER),('Active orders',s['active_orders'],AMBER),('Total sales',db.money(s['sales']),GOLD)]):self.card(stats,a,b,c).grid(row=0,column=i,sticky='ew',padx=5)
        ctk.CTkLabel(root,text='Dining area — select a live table',font=('Segoe UI',18,'bold')).pack(anchor='w',pady=(24,9));floor=ctk.CTkFrame(root,fg_color='#181818',corner_radius=12);floor.pack(fill='both',expand=True);[floor.grid_columnconfigure(i,weight=1) for i in range(4)]
        for i,t in enumerate(db.tables()):
            colors={'AVAILABLE':GREEN,'OCCUPIED':RED,'RESERVED':AMBER,'OUT_OF_SERVICE':'#666'};f=ctk.CTkFrame(floor,fg_color=colors.get(t['status'],CARD),corner_radius=10);f.grid(row=i//4,column=i%4,sticky='nsew',padx=12,pady=12);ctk.CTkLabel(f,text=t['label'],font=('Segoe UI',20,'bold')).pack(pady=(13,2));ctk.CTkLabel(f,text=t['status'].title(),font=('Segoe UI',12,'bold')).pack();ctk.CTkLabel(f,text=f"Pending: {t['pending']}  •  {db.money(t['total'])}\nWaiter: {t['waiter']}",font=('Segoe UI',10)).pack(pady=(5,13))
    def kitchen(self):
        self.clear();self.header('Kitchen order queue','FIFO workflow: finish the active order before starting the next one.')
        root=ctk.CTkFrame(self.body,fg_color=BG);root.pack(fill='both',expand=True,padx=22,pady=18);orders=db.kitchen_orders();active=next((o for o in orders if o['queue_status']=='PREPARING'),None);ctk.CTkLabel(root,text='Active order' if active else 'No order currently being prepared',font=('Segoe UI',19,'bold'),text_color=GOLD).pack(anchor='w')
        if active:self.order_panel(root,active,'Mark as Ready',lambda: self.action(db.mark_ready,active['id'],self.kitchen),GREEN)
        ctk.CTkLabel(root,text='Waiting queue',font=('Segoe UI',18,'bold')).pack(anchor='w',pady=(18,6));box=ctk.CTkScrollableFrame(root,fg_color='#181818');box.pack(fill='both',expand=True)
        for o in orders:
            if o['queue_status']=='WAITING':self.order_panel(box,o,'Start Preparing',lambda x=o['id']:self.action(db.start_order,x,self.kitchen),GOLD)
    def order_panel(self,p,o,label,cmd,color):
        f=ctk.CTkFrame(p,fg_color=CARD,corner_radius=10);f.pack(fill='x',padx=8,pady=7);ctk.CTkLabel(f,text=f"{o['order_no']}  •  {o['label']}",font=('Segoe UI',15,'bold'),text_color=GOLD).pack(anchor='w',padx=14,pady=(10,2));ctk.CTkLabel(f,text=o['items']+ (f"\nNote: {o['notes']}" if o['notes'] else ''),text_color=MUTED,justify='left').pack(anchor='w',padx=14,pady=(0,8));self.button(f,label,cmd,fg=color,height=30).pack(anchor='e',padx=12,pady=(0,10))
    def action(self,func,arg,back):
        try:func(arg);back()
        except Exception as e:messagebox.showerror('Workflow rule',str(e))
    def waiter(self):
        self.clear();self.header('Waiter service & checkout','Verify every food item before an order becomes delivered.')
        root=ctk.CTkFrame(self.body,fg_color=BG);root.pack(fill='both',expand=True,padx=22,pady=18);tabs=ctk.CTkTabview(root,fg_color='#181818',segmented_button_selected_color=GOLD);tabs.pack(fill='both',expand=True);ready=tabs.add('Ready for delivery');check=tabs.add('Checkout confirmation')
        orders=db.ready_orders()
        if not orders:ctk.CTkLabel(ready,text='No ready orders right now.',text_color=MUTED).pack(pady=35)
        for o in orders:
            f=ctk.CTkFrame(ready,fg_color=CARD);f.pack(fill='x',padx=10,pady=8);ctk.CTkLabel(f,text=f"{o['order_no']} • {o['label']}\n{o['items']}",justify='left',font=('Segoe UI',14,'bold')).pack(anchor='w',padx=12,pady=10);self.button(f,'Verify & Serve Items',lambda x=o:self.serve_dialog(x),height=32).pack(anchor='e',padx=12,pady=(0,10))
        paid=db.bills('PAID');
        if not paid:ctk.CTkLabel(check,text='No paid tables awaiting checkout.',text_color=MUTED).pack(pady=35)
        for b in paid:
            f=ctk.CTkFrame(check,fg_color=CARD);f.pack(fill='x',padx=10,pady=8);ctk.CTkLabel(f,text=f"{b['label']}  •  {b['bill_no']}  •  {db.money(b['total_paise'])}",font=('Segoe UI',14,'bold')).pack(side='left',padx=12,pady=14);self.button(f,'Confirm physical checkout',lambda x=b['label']:self.action(db.confirm_checkout,x,self.waiter),height=32).pack(side='right',padx=12)
    def serve_dialog(self,o):
        win=ctk.CTkToplevel(self);win.title(f"Verify {o['order_no']}");win.geometry('460x420');win.configure(fg_color=BG);ctk.CTkLabel(win,text=f"{o['order_no']} — {o['label']}",font=('Segoe UI',19,'bold'),text_color=GOLD).pack(pady=18);vars=[]
        for it in db.order_items(o['id']):v=ctk.BooleanVar(value=bool(it['served']));ctk.CTkCheckBox(win,text=f"{it['item_name']} × {it['quantity']}",variable=v).pack(anchor='w',padx=35,pady=8);vars.append((it['id'],v))
        def confirm():
            done=db.serve_items(o['id'],[x for x,v in vars if v.get()]);messagebox.showinfo('Delivery updated','Order delivered.' if done else 'Saved. Check all remaining items before delivery.');win.destroy();self.waiter()
        self.button(win,'Confirm checked items',confirm,height=40).pack(side='bottom',fill='x',padx=25,pady=24)
    def billing(self):
        self.clear();self.header('Billing & payments','Combined final bills use all orders from a table session.')
        root=ctk.CTkFrame(self.body,fg_color=BG);root.pack(fill='both',expand=True,padx=22,pady=18);top=ctk.CTkFrame(root,fg_color='transparent');top.pack(fill='x');table=ctk.CTkOptionMenu(top,values=[t['label'] for t in db.tables()],fg_color=CARD,button_color=GOLD);table.set('T01');table.pack(side='left')
        def generate():
            try:b=db.bill_for_table(table.get());messagebox.showinfo('Bill ready',f"{b['bill_no']} generated: {db.money(b['total_paise'])}");self.billing()
            except Exception as e:messagebox.showerror('Billing',str(e))
        self.button(top,'Generate / refresh bill',generate,width=190).pack(side='left',padx=10);tabs=ctk.CTkTabview(root,fg_color='#181818',segmented_button_selected_color=GOLD);tabs.pack(fill='both',expand=True,pady=(14,0))
        for title,status in [('Pending bills','PENDING'),('Paid — awaiting checkout','PAID'),('Closed bills','CLOSED')]:
            page=tabs.add(title);rows=db.bills(status)
            if not rows:ctk.CTkLabel(page,text='No bills in this list.',text_color=MUTED).pack(pady=30)
            for b in rows:
                f=ctk.CTkFrame(page,fg_color=CARD);f.pack(fill='x',padx=10,pady=7);ctk.CTkLabel(f,text=f"{b['bill_no']}  •  {b['label']}  •  {b['customer_name'] or 'Guest'}\nSubtotal {db.money(b['subtotal_paise'])}  | GST {db.money(b['tax_paise'])}  | Total {db.money(b['total_paise'])}",justify='left',font=('Segoe UI',13,'bold')).pack(side='left',padx=12,pady=10)
                self.button(f,'PDF',lambda x=b['id']:self.invoice(x),width=52,height=32,fg='#555').pack(side='right',padx=8)
                if status=='PENDING':
                    method=ctk.CTkOptionMenu(f,values=['Cash','Card','UPI'],width=85,fg_color='#333',button_color=GOLD);method.pack(side='right',padx=8);self.button(f,'Record payment',lambda x=b, m=method:self.pay(x['id'],m.get()),width=130,height=32).pack(side='right')
    def pay(self,bid,method):
        try:db.pay_bill(bid,method);messagebox.showinfo('Payment recorded','Bill is paid and awaits waiter checkout confirmation.');self.billing()
        except Exception as e:messagebox.showerror('Payment',str(e))
    def invoice(self,bid):
        try:
            from report_generator import generate_invoice
            messagebox.showinfo('Invoice created',f'Saved locally to:\n{generate_invoice(bid)}')
        except Exception as e: messagebox.showerror('Invoice',str(e))

if __name__=='__main__':DineFlow().mainloop()
