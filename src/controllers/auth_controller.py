from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_user, logout_user, current_user, login_required
from models.uporabniki import User
import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registracija', methods=['GET', 'POST'])
def register():
    """Registracija uporabnikoa"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        #TODO: Implementirati email storitev, pomozne metode obstajajo
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # ujemanje uporabniškega gesla
        if password != confirm_password:
            flash('Gesli se ne ujemata', 'danger')
            return render_template('registracija.html')
        
        # ustvari objekt uporabnika
        user = User(username=username, email=email)
        
        # registritraj uproabnika
        #conn = g.db
        #success, message = user.register(conn, password)
        
        try:
            conn = g.db
            print(f"DB povezava: {conn}")
            success, message = user.register(conn, password)
            print(f"Registracija: Uspesno?={success}, msg={message}")
            
            if success:
                flash(message, 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(message, 'danger')
        except Exception as e:
            print(f"EXCEPTION in register: {e}")
            import traceback
            traceback.print_exc()
            flash('Napaka pri registraciji', 'danger')
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('registracija.html')

@auth_bp.route('/prijava', methods=['GET', 'POST'])
def login():
    """Prijava uporabnika"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        conn = g.db
        user, success, message = User.login(conn, username_or_email, password)
        
        if success:
            login_user(user, remember=remember)
            flash(message, 'success')
            
            # preusmeri uporabnika na defualt spletno stran
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash(message, 'danger')
    
    return render_template('prijava.html')

@auth_bp.route('/odjava')
@login_required
def logout():
    """Odjava uporabnika"""
    logout_user()
    flash('Uspešno ste se odjavili', 'info')
    return redirect(url_for('home'))

@auth_bp.route('/pozabljenogeslo', methods=['GET', 'POST'])
def forgot_password():
    """
    Resetiranje uporabniškega gesla
    TODO: Implementirati email storitev, pomozne metode obstajajo
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not User.validate_email(email):
            flash('Neveljaven email naslov', 'danger')
            return render_template('pozabljenogeslo.html')
        
        conn = g.db
        user = User.find_by_email(conn, email)
        
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            user.save_reset_token(conn)
            
            # Create reset URL
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # Send email
            success, message = user.send_reset_email(reset_url)
            
            if success:
                flash('Navodila za ponastavitev gesla so bila poslana na vaš email', 'info')
            else:
                flash('Napaka pri pošiljanju emaila. Prosimo, poskusite kasneje.', 'danger')
        else:
            # Don't reveal if email exists
            flash('Če email obstaja v naši bazi, boste prejeli navodila za ponastavitev', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('pozabljenogeslo.html')

@auth_bp.route('/ponastavi-geslo/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Ponastavitev gesla uporabnika z unikatnim tokenom"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    conn = g.db
    user = User.find_by_reset_token(conn, token)
    
    if not user:
        flash('Neveljavna ali potekla povezava za ponastavitev gesla', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Gesli se ne ujemata', 'danger')
        else:
            success, message = user.reset_password(conn, password)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(message, 'danger')
    
    return render_template('reset_password.html', token=token)

@auth_bp.route('/spremeni-geslo', methods=['GET', 'POST'])
@login_required
def change_password():
    """Spremeni geslo uporabnika (prijavljenega)"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Preveri veljavnost trenutnega gesla
        if not current_user.verify_password(current_password):
            flash('Trenutno geslo ni pravilno', 'danger')
            return render_template('reset_password.html')
        
        # Preveri ali se nova gesla ujemata
        if new_password != confirm_password:
            flash('Novi gesli se ne ujemata', 'danger')
            return render_template('reset_password.html')
        
        # posodobi geslo
        conn = g.db
        success, message = current_user.reset_password(conn, new_password)
        
        if success:
            flash('Geslo uspešno spremenjeno', 'success')
            return redirect(url_for('profile'))
        else:
            flash(message, 'danger')
    
    return render_template('change_password.html')