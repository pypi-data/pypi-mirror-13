class AlreadyRegisteredMylistError(Exception):
    """
    既に登録されている mylist が登録されそうになったとき呼ばれる
    """

class NotRegisteredMylistError(Exception):
    """
    登録されていない mylist が削除されそうになったとき呼ばれる
    """

class NotInitError(Exception):
    """
    gazeru init してないときに呼ばれる
    """
